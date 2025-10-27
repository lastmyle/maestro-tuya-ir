"""
/api/identify endpoint - Identify device from Tuya IR code.
"""

from fastapi import APIRouter, HTTPException

from app.core.protocol_timings import identify_protocol, parse_hvac_state
from app.core.tuya import decode_tuya_ir
from app.models.request import IdentifyRequest
from app.models.response import ErrorResponse, IdentifyResponse

router = APIRouter()


@router.post(
    "/identify", response_model=IdentifyResponse, responses={404: {"model": ErrorResponse}}
)
async def identify(request: IdentifyRequest):
    """
    Identify HVAC device from a Tuya IR code.

    Args:
        request: IdentifyRequest with Tuya code and optional manufacturer hint

    Returns:
        IdentifyResponse with manufacturer, protocol, and capabilities

    Raises:
        HTTPException: If protocol cannot be identified
    """
    try:
        # Decode to timings
        timings = decode_tuya_ir(request.tuyaCode)

        # Identify protocol
        protocol_data = identify_protocol(timings)

        # Parse current state
        detected_state = parse_hvac_state(timings, protocol_data["protocol"])

        return IdentifyResponse(
            success=True,
            manufacturer=protocol_data["manufacturer"],
            protocol=protocol_data["protocol"],
            modelFamily=None,  # Could be enhanced with model detection
            capabilities=protocol_data["capabilities"],
            detectedState=detected_state,
        )

    except ValueError as e:
        error_msg = str(e)
        if "Could not identify" in error_msg:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": "PROTOCOL_NOT_FOUND",
                    "message": "Could not identify IR protocol from provided code",
                    "suggestions": [
                        "Try providing manufacturer hint",
                        "Ensure code is complete and valid",
                    ],
                },
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "INVALID_TUYA_CODE",
                    "message": "Invalid Tuya IR code",
                    "details": error_msg,
                },
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": str(e),
            },
        )
