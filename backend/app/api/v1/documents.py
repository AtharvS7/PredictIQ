"""
PredictIQ API — Document Endpoints
Handles document upload (direct file + metadata) and retrieval.
Files are stored as BYTEA in Neon PostgreSQL.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
import structlog
import json
from app.core.security import get_current_user, CurrentUser
from app.core.database import get_db
from app.models.document import DocumentUploadRequest, DocumentMetadata

router = APIRouter()
logger = structlog.get_logger()


@router.post("/documents/upload", response_model=DocumentMetadata)
async def confirm_document_upload(
    request: DocumentUploadRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """
    Confirm a document upload — stores metadata in the database.
    (Legacy endpoint for metadata-only confirmation.)
    """
    try:
        pool = await get_db()
        row = await pool.fetchrow(
            """INSERT INTO document_uploads (user_id, storage_path, original_filename, file_size_bytes, mime_type, status)
               VALUES ($1, $2, $3, $4, $5, 'uploaded')
               RETURNING *""",
            user.id,
            request.storage_path,
            request.original_filename,
            request.file_size_bytes,
            request.mime_type,
        )

        if not row:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save document metadata",
            )

        logger.info("document_uploaded", doc_id=str(row["id"]), user_id=user.id)

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
        logger.error("document_upload_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}",
        )


@router.post("/documents/upload-file", response_model=DocumentMetadata)
async def upload_document_file(
    file: UploadFile = File(...),
    user: CurrentUser = Depends(get_current_user),
):
    """
    Upload a document file directly to the backend.
    File bytes are stored in the database (BYTEA column).
    """
    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        # Validate file size (10 MB limit)
        if file_size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large. Maximum size is 10 MB.",
            )

        # Validate MIME type
        allowed_types = [
            "application/pdf",
            "text/plain",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
        ]
        mime = file.content_type or "application/octet-stream"
        if mime not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file type: {mime}. Allowed: PDF, DOCX, TXT",
            )

        pool = await get_db()
        storage_path = f"{user.id}/{file.filename}"

        row = await pool.fetchrow(
            """INSERT INTO document_uploads
               (user_id, storage_path, original_filename, file_size_bytes, mime_type, status, file_data)
               VALUES ($1, $2, $3, $4, $5, 'uploaded', $6)
               RETURNING id, user_id, storage_path, original_filename, file_size_bytes,
                         mime_type, status, parsed_text_preview, created_at""",
            user.id,
            storage_path,
            file.filename,
            file_size,
            mime,
            file_content,
        )

        if not row:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save document",
            )

        logger.info("document_file_uploaded", doc_id=str(row["id"]), user_id=user.id, size=file_size)

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
            detail=f"Upload failed: {str(e)}",
        )


@router.get("/documents/{document_id}", response_model=DocumentMetadata)
async def get_document(
    document_id: str,
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
            detail=str(e),
        )


@router.post("/documents/{document_id}/extract")
async def extract_document_parameters(
    document_id: str,
    user: CurrentUser = Depends(get_current_user),
):
    """
    Run NLP extraction on an uploaded document and return extracted parameters.
    Called by the frontend after upload to pre-fill the Step 2 form.
    """
    from app.services.document_parser import document_parser
    from app.services.nlp_extractor import nlp_extractor

    try:
        pool = await get_db()
        doc = await pool.fetchrow(
            """SELECT id, file_data, mime_type, original_filename
               FROM document_uploads
               WHERE id = $1 AND user_id = $2""",
            document_id,
            user.id,
        )

        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # Parse document to extract raw text
        file_data = doc["file_data"]
        if not file_data:
            raise HTTPException(status_code=400, detail="No file data stored")

        try:
            parse_result = document_parser.parse(bytes(file_data), doc["mime_type"])
        except Exception as parse_err:
            logger.warning("document_parse_error_extract", error=str(parse_err))
            raise HTTPException(
                status_code=422,
                detail=f"Could not parse document: {str(parse_err)}",
            )

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
            detail=f"Extraction failed: {str(e)}",
        )
