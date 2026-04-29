"""
Predictify Pydantic Models — Document
Schemas for document upload and metadata.
"""
from pydantic import BaseModel, Field
from typing import Optional


class DocumentUploadRequest(BaseModel):
    """Request body for confirming a document upload."""
    storage_path: str
    original_filename: str
    file_size_bytes: int = Field(..., gt=0)
    mime_type: str


class DocumentMetadata(BaseModel):
    """Document metadata returned from the API."""
    id: str
    user_id: str
    storage_path: str
    original_filename: str
    file_size_bytes: int
    mime_type: str
    status: str
    parsed_text_preview: Optional[str] = None
    created_at: str


class DocumentParseResult(BaseModel):
    """Result of parsing a document for text extraction."""
    raw_text: str
    text_preview: str
    word_count: int
    page_count: Optional[int] = None
