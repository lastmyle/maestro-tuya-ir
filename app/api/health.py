"""
/api/health endpoint - Health check and supported manufacturers.
"""

from fastapi import APIRouter

from app.core.protocol_timings import get_supported_manufacturers
from app.models.response import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    """
    Health check endpoint.

    Returns:
        HealthResponse with service status and supported manufacturers
    """
    return HealthResponse(
        status="ok",
        supportedManufacturers=get_supported_manufacturers(),
        version="1.0.0",
    )
