"""
PredictIQ API — Document Endpoints
Handles document upload metadata and retrieval.
"""
from fastapi import APIRouter, Depends, HTTPException, status
import structlog
from app.core.security import get_current_user, CurrentUser
from app.core.supabase import get_supabase
from app.models.document import DocumentUploadRequest, DocumentMetadata

router = APIRouter()
logger = structlog.get_logger()


@router.post("/documents/upload", response_model=DocumentMetadata)
async def confirm_document_upload(
    request: DocumentUploadRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """
    Confirm a document upload after file is stored in Supabase Storage.
    Stores metadata in the document_uploads table.
    """
    try:
        supabase = get_supabase()
        result = supabase.table("document_uploads").insert({
            "user_id": user.id,
            "storage_path": request.storage_path,
            "original_filename": request.original_filename,
            "file_size_bytes": request.file_size_bytes,
            "mime_type": request.mime_type,
            "status": "uploaded",
        }).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save document metadata",
            )

        doc = result.data[0]
        logger.info("document_uploaded", doc_id=doc["id"], user_id=user.id)

        return DocumentMetadata(
            id=doc["id"],
            user_id=doc["user_id"],
            storage_path=doc["storage_path"],
            original_filename=doc["original_filename"],
            file_size_bytes=doc["file_size_bytes"],
            mime_type=doc["mime_type"],
            status=doc["status"],
            parsed_text_preview=doc.get("parsed_text_preview"),
            created_at=doc["created_at"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("document_upload_error", error=str(e))
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
        supabase = get_supabase()
        result = supabase.table("document_uploads").select("*").eq(
            "id", document_id
        ).eq("user_id", user.id).single().execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        doc = result.data
        return DocumentMetadata(
            id=doc["id"],
            user_id=doc["user_id"],
            storage_path=doc["storage_path"],
            original_filename=doc["original_filename"],
            file_size_bytes=doc["file_size_bytes"],
            mime_type=doc["mime_type"],
            status=doc["status"],
            parsed_text_preview=doc.get("parsed_text_preview"),
            created_at=doc["created_at"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("document_get_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
