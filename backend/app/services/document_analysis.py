"""Shared, fail-closed contract for analyzing stored documents."""
from fastapi import HTTPException
from starlette.concurrency import run_in_threadpool

from app.services.document_parser import document_parser
from app.services.storage_service import storage_service

MAX_DOCUMENT_BYTES = 10 * 1024 * 1024


async def parse_stored_document(doc, user_id: str) -> dict:
    if doc.get("status") not in ("uploaded", "parsed", "complete"):
        raise HTTPException(status_code=409, detail="Document is not ready for analysis")
    key = doc.get("storage_path")
    try:
        owned = storage_service.belongs_to_user(key, user_id)
    except ValueError:
        owned = False
    if not owned:
        raise HTTPException(status_code=409, detail="Document storage reference is invalid")
    try:
        content = await storage_service.download(key)
    except Exception:
        raise HTTPException(status_code=503, detail="Document storage is unavailable") from None
    if content is None:
        raise HTTPException(status_code=409, detail="Document file is missing; upload it again")
    if not content or len(content) > MAX_DOCUMENT_BYTES:
        raise HTTPException(status_code=422, detail="Document file is empty or too large")
    try:
        result = await run_in_threadpool(document_parser.parse, content, doc["mime_type"])
    except ValueError:
        raise HTTPException(status_code=422, detail="Could not parse document; upload a valid PDF, DOCX or TXT file") from None
    if len(result.get("raw_text", "").strip()) < 20:
        raise HTTPException(status_code=422, detail="Document contains too little text for extraction")
    return result
