"""
Predictify API — Export Endpoints
PDF and JSON export for estimates with multi-currency support.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
import io
import json
import structlog

from app.core.security import get_current_user, CurrentUser
from app.core.database import get_db
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
        pool = await get_db()
        row = await pool.fetchrow(
            """SELECT * FROM estimates WHERE id = $1 AND user_id = $2""",
            estimate_id, user.id,
        )

        if not row:
            raise HTTPException(status_code=404, detail="Estimate not found")

        inputs_json = row.get("inputs_json") or {}
        outputs_json = row.get("outputs_json") or {}
        if isinstance(inputs_json, str):
            inputs_json = json.loads(inputs_json)
        if isinstance(outputs_json, str):
            outputs_json = json.loads(outputs_json)

        estimate = {
            "project_name": row["project_name"],
            "inputs": inputs_json,
            "outputs": outputs_json,
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
        filename = f"Predictify_Estimate_{safe_id}_{currency_code}.pdf"
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
        pool = await get_db()
        row = await pool.fetchrow(
            """SELECT * FROM estimates WHERE id = $1 AND user_id = $2""",
            estimate_id, user.id,
        )

        if not row:
            raise HTTPException(status_code=404, detail="Estimate not found")

        # Convert asyncpg Record to dict
        result_dict = dict(row)
        # Convert non-JSON-serializable types
        for key, value in result_dict.items():
            if hasattr(value, "isoformat"):
                result_dict[key] = value.isoformat()
            elif isinstance(value, bytes):
                del result_dict[key]  # Don't include binary data in JSON export

        return JSONResponse(content=result_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("json_export_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
