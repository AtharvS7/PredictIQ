"""
PredictIQ API — Health Check
Exposes model status, training metrics, and dataset info.
"""
from fastapi import APIRouter
from ml.inference import predictor

router = APIRouter()


@router.get("/health")
async def health_check():
    """System health check with model status and training metrics."""
    model_info = predictor.get_model_info()
    return {
        "status": "ok",
        "version": "2.0.0",
        **model_info,
    }
