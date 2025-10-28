"""
/api/encode endpoint - Encode single HVAC command to Tuya format.
"""

from fastapi import APIRouter, HTTPException

from app.core.generator import generate_command
from app.core.tuya_encoder import decode_tuya_ir
from app.models.request import EncodeRequest
from app.models.response import EncodeResponse, ErrorResponse

router = APIRouter()


@router.post("/encode", response_model=EncodeResponse, responses={422: {"model": ErrorResponse}})
async def encode(request: EncodeRequest):
    """
    Encode a single HVAC command to Tuya format.

    Args:
        request: EncodeRequest with manufacturer, protocol, and command parameters

    Returns:
        EncodeResponse with Tuya code and timings

    Raises:
        HTTPException: If parameters are invalid or protocol is not supported
    """
    try:
        # Generate the command
        tuya_code = generate_command(
            protocol=request.protocol,
            power=request.command.power,
            mode=request.command.mode,
            temperature=request.command.temperature,
            fan=request.command.fan,
            swing=request.command.swing,
        )

        # Decode back to get timings for response
        timings = decode_tuya_ir(tuya_code)

        return EncodeResponse(
            success=True,
            tuyaCode=tuya_code,
            timings=timings,
            timingsLength=len(timings),
        )

    except ValueError as e:
        error_msg = str(e)
        if "Unsupported protocol" in error_msg:
            from app.core.protocol_timings import get_supported_manufacturers

            raise HTTPException(
                status_code=422,
                detail={
                    "success": False,
                    "error": "UNSUPPORTED_PROTOCOL",
                    "message": error_msg,
                    "supportedManufacturers": get_supported_manufacturers(),
                },
            )
        else:
            raise HTTPException(
                status_code=422,
                detail={
                    "success": False,
                    "error": "INVALID_PARAMETERS",
                    "message": "Invalid command parameters",
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
