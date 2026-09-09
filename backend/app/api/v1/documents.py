"""
Predictify API — Document Endpoints
Handles document upload (direct file + metadata) and retrieval.
Files are stored in object storage; PostgreSQL holds metadata.
"""
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.database import get_db
from app.core.security import CurrentUser, get_current_user, require_role
from app.models.document import DocumentMetadata, DocumentUploadRequest
from app.services.document_analysis import MAX_DOCUMENT_BYTES, parse_stored_document
from app.services.document_parser import document_parser
from app.services.storage_service import storage_service

router = APIRouter()
logger = structlog.get_logger()


@router.post("/documents/upload", response_model=DocumentMetadata)
async def confirm_document_upload(
    request: DocumentUploadRequest,
    user: CurrentUser = Depends(require_role("editor")),
):
    """
    Confirm a document upload — stores metadata in the database.
    (Legacy endpoint for metadata-only confirmation.)
    """
    raise HTTPException(status_code=410, detail="Use /documents/upload-file to upload document bytes")


@router.post("/documents/upload-file", response_model=DocumentMetadata)
async def upload_document_file(
    file: UploadFile = File(...),
    user: CurrentUser = Depends(require_role("editor")),
):
    """
    Upload a document file.
    Files are stored via the configured storage backend (local filesystem or S3).
    Only metadata is saved in the database.
    """
    storage_key = None
    saved = False
    try:
        # Bounded read, including when Content-Length is absent or dishonest.
        file_content = await file.read(MAX_DOCUMENT_BYTES + 1)
        file_size = len(file_content)

        # Validate file size (10 MB limit)
        if file_size > MAX_DOCUMENT_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large. Maximum size is 10 MB.",
            )
        if file_size == 0:
            raise HTTPException(status_code=422, detail="Document file is empty")
        if not file.filename or len(file.filename) > 255:
            raise HTTPException(status_code=422, detail="Filename must contain 1 to 255 characters")

        # Validate MIME type
        allowed_types = [
            "application/pdf",
            "text/plain",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]
        mime = file.content_type or "application/octet-stream"
        if mime not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Unsupported file type. Allowed: PDF, DOCX, TXT",
            )

        try:
            document_parser.validate_content(file_content, mime)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid document content") from None

        # Upload to storage backend (local or S3)
        storage_key = storage_service.generate_key(user.id, file.filename)
        await storage_service.upload(file_content, storage_key, mime)

        # Save metadata to database (no BYTEA — file data is in object storage)
        pool = await get_db()
        row = await pool.fetchrow(
            """INSERT INTO document_uploads
               (user_id, storage_path, original_filename, file_size_bytes, mime_type, status)
               VALUES ($1, $2, $3, $4, $5, 'uploaded')
               RETURNING id, user_id, storage_path, original_filename, file_size_bytes,
                         mime_type, status, parsed_text_preview, created_at""",
            user.id,
            storage_key,
            file.filename,
            file_size,
            mime,
        )

        if not row:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save document",
            )
        saved = True

        logger.info(
            "document_file_uploaded",
            doc_id=str(row["id"]),
            user_id=user.id,
            size=file_size,
            storage_key=storage_key,
        )

        return DocumentMetadata(
            id=str(row["id"]),
            user_id=row["user_id"],
            storage_path=row["storage_path"],
            original_filename=row["original_filename"],
            file_size_bytes=row["file_size_bytes"],
            mime_type=row["mime_type"],
            status=row["status"],
            parsed_text_preview=row.get("parsed_text_preview"),
            created_at=str(row["created_at"]),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("document_file_upload_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document upload failed",
        )
    finally:
        await file.close()
        if storage_key and not saved:
            try:
                await storage_service.delete(storage_key)
            except Exception:
                logger.error("document_upload_cleanup_failed")


@router.get("/documents/{document_id}", response_model=DocumentMetadata)
async def get_document(
    document_id: UUID,
    user: CurrentUser = Depends(get_current_user),
):
    """Retrieve document metadata by ID."""
    try:
        pool = await get_db()
        row = await pool.fetchrow(
            """SELECT id, user_id, storage_path, original_filename, file_size_bytes,
                      mime_type, status, parsed_text_preview, created_at
               FROM document_uploads
               WHERE id = $1 AND user_id = $2""",
            document_id,
            user.id,
        )

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        return DocumentMetadata(
            id=str(row["id"]),
            user_id=row["user_id"],
            storage_path=row["storage_path"],
            original_filename=row["original_filename"],
            file_size_bytes=row["file_size_bytes"],
            mime_type=row["mime_type"],
            status=row["status"],
            parsed_text_preview=row.get("parsed_text_preview"),
            created_at=str(row["created_at"]),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("document_get_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve document",
        )


@router.post("/documents/{document_id}/extract")
async def extract_document_parameters(
    document_id: UUID,
    user: CurrentUser = Depends(require_role("editor")),
):
    """
    Run NLP extraction on an uploaded document and return extracted parameters.
    Called by the frontend after upload to pre-fill the Step 2 form.
    """
    from app.services.nlp_extractor import nlp_extractor

    try:
        pool = await get_db()
        doc = await pool.fetchrow(
            """SELECT id, storage_path, status, mime_type, original_filename
               FROM document_uploads
               WHERE id = $1 AND user_id = $2""",
            document_id,
            user.id,
        )

        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        parse_result = await parse_stored_document(doc, user.id)
        raw_text = parse_result.get("raw_text", "")
        if not raw_text or len(raw_text.strip()) < 20:
            raise HTTPException(
                status_code=422,
                detail="Document contains too little text for extraction",
            )

        # Run NLP extraction
        extracted = nlp_extractor.extract(raw_text)

        # Map to frontend-friendly format
        result = {
            "project_name": extracted.get("project_name", {}).get("value", ""),
            "project_type": extracted.get("project_type", {}).get("value", "Web App"),
            "team_size": extracted.get("team_size", {}).get("value", 5),
            "duration_months": extracted.get("duration_months", {}).get("value", 6.0),
            "complexity": extracted.get("complexity", {}).get("value", "Medium"),
            "methodology": extracted.get("methodology", {}).get("value", "Agile"),
            "tech_stack": extracted.get("tech_stack", {}).get("value", []),
            "integration_count": extracted.get("integration_count", {}).get("value", 2),
            "volatility_score": extracted.get("volatility_score", {}).get("value", 3),
            "team_experience": extracted.get("team_experience", {}).get("value", 3.0),
            "feature_count": extracted.get("feature_count", {}).get("value", 10),
            # Include raw confidence scores for transparency
            "confidence": {
                k: extracted.get(k, {}).get("confidence", 0.0)
                for k in extracted
            },
            "word_count": parse_result.get("word_count", 0),
        }

        logger.info(
            "document_nlp_extracted",
            doc_id=document_id,
            project_name=result["project_name"],
            tech_count=len(result["tech_stack"]),
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error("document_extract_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document extraction failed",
        )
