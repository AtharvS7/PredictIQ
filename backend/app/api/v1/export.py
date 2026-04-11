"""
PredictIQ API — Export Endpoints
PDF and JSON export for estimates.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import io
import structlog

from app.core.security import get_current_user, CurrentUser
from app.core.supabase import get_supabase
from app.services.export_service import generate_pdf_report

router = APIRouter()
logger = structlog.get_logger()


@router.get("/estimates/{estimate_id}/export/pdf")
async def export_pdf(
    estimate_id: str,
    user: CurrentUser = Depends(get_current_user),
):
    """Generate and stream a branded PDF report."""
    try:
        supabase = get_supabase()
        result = supabase.table("estimates").select("*").eq(
            "id", estimate_id
        ).eq("user_id", user.id).single().execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Estimate not found")

        row = result.data
        estimate = {
            "project_name": row["project_name"],
            "inputs": row.get("inputs_json", {}),
            "outputs": row.get("outputs_json", {}),
        }

        pdf_bytes = generate_pdf_report(estimate)

        filename = f"PredictIQ_{row['project_name'].replace(' ', '_')}_Report.pdf"
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("pdf_export_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"PDF export failed: {str(e)}")


@router.get("/estimates/{estimate_id}/export/json")
async def export_json(
    estimate_id: str,
    user: CurrentUser = Depends(get_current_user),
):
    """Export estimate as JSON."""
    try:
        supabase = get_supabase()
        result = supabase.table("estimates").select("*").eq(
            "id", estimate_id
        ).eq("user_id", user.id).single().execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Estimate not found")

        return JSONResponse(content=result.data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("json_export_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
