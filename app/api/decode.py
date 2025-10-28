"""
/api/decode endpoint - Decode Tuya IR codes to raw timings.
"""

from fastapi import APIRouter, HTTPException

from app.core.protocol_timings import identify_protocol, parse_hvac_state
from app.core.tuya_encoder import decode_tuya_ir
from app.models.request import DecodeRequest
from app.models.response import DecodeResponse, ErrorResponse, ProtocolInfo

router = APIRouter()


@router.post("/decode", response_model=DecodeResponse, responses={400: {"model": ErrorResponse}})
async def decode(request: DecodeRequest):
    """
    Decode a Tuya IR code to raw timings and identify the protocol.

    Args:
        request: DecodeRequest containing the Tuya code

    Returns:
        DecodeResponse with timings, protocol info, and decoded state

    Raises:
        HTTPException: If the code cannot be decoded
    """
    try:
        # Decode to timings
        timings = decode_tuya_ir(request.tuyaCode)

        # Try to identify protocol
        protocol_info = None
        state = None

        try:
            protocol_data = identify_protocol(timings)
            protocol_info = ProtocolInfo(
                name=protocol_data["protocol"],
                manufacturer=protocol_data["manufacturer"],
                confidence=protocol_data["confidence"],
            )

            # Try to parse state
            state = parse_hvac_state(timings, protocol_data["protocol"])

        except ValueError:
            # Protocol identification failed - return timings only
            pass

        return DecodeResponse(success=True, timings=timings, protocol=protocol_info, state=state)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "INVALID_TUYA_CODE",
                "message": "Invalid Tuya IR code",
                "details": str(e),
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
