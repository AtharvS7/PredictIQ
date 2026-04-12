"""
PredictIQ API — Export Endpoints
PDF and JSON export for estimates with multi-currency support.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
import io
import structlog

from app.core.security import get_current_user, CurrentUser
from app.core.supabase import get_supabase_admin
from app.services.export_service import generate_pdf_report
from app.services.currency_service import currency_service

router = APIRouter()
logger = structlog.get_logger()


@router.get("/estimates/{estimate_id}/export/pdf")
async def export_pdf(
    estimate_id: str,
    currency: str = Query("USD", description="Target currency code (e.g., USD, INR, EUR)"),
    user: CurrentUser = Depends(get_current_user),
):
    """Generate and stream a branded PDF report in the selected currency."""
    try:
        supabase = get_supabase_admin()
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

        # Fetch live exchange rate for the selected currency
        currency_code = currency.upper().strip()
        exchange_rate = 1.0
        if currency_code != "USD":
            rate = await currency_service.get_rate(currency_code)
            if rate is not None:
                exchange_rate = rate
            else:
                logger.warning(
                    "pdf_export_unknown_currency",
                    currency=currency_code,
                    message="Falling back to USD",
                )
                currency_code = "USD"

        pdf_bytes = generate_pdf_report(
            estimate,
            currency_code=currency_code,
            exchange_rate=exchange_rate,
        )

        safe_id = estimate_id[:8] if len(estimate_id) >= 8 else estimate_id
        filename = f"PredictIQ_Estimate_{safe_id}_{currency_code}.pdf"
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
        supabase = get_supabase_admin()
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
