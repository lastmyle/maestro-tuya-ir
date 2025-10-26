"""
/api/generate endpoint - Generate complete HVAC command sets.
"""

from fastapi import APIRouter, HTTPException

from app.core.generator import HVACCodeGenerator
from app.core.protocols import get_protocol_by_name
from app.models.request import GenerateRequest
from app.models.response import ErrorResponse, GenerateResponse

router = APIRouter()


@router.post(
    "/generate", response_model=GenerateResponse, responses={422: {"model": ErrorResponse}}
)
async def generate(request: GenerateRequest):
    """
    Generate complete HVAC command set for a manufacturer/protocol.

    Args:
        request: GenerateRequest with manufacturer, protocol, and optional filters

    Returns:
        GenerateResponse with all generated commands

    Raises:
        HTTPException: If manufacturer/protocol is not supported
    """
    try:
        # Validate protocol exists
        protocol_def = get_protocol_by_name(request.protocol)
        if not protocol_def:
            from app.core.protocols import get_supported_manufacturers

            raise HTTPException(
                status_code=422,
                detail={
                    "success": False,
                    "error": "UNSUPPORTED_PROTOCOL",
                    "message": f"Protocol '{request.protocol}' not supported",
                    "supportedManufacturers": get_supported_manufacturers(),
                },
            )

        # Create generator
        generator = HVACCodeGenerator(request.protocol)

        # Parse filters
        modes = None
        temp_range = None
        fan_speeds = None

        if request.filter:
            modes = request.filter.modes
            if request.filter.tempRange:
                temp_range = tuple(request.filter.tempRange)
            fan_speeds = request.filter.fanSpeeds

        # Generate commands
        commands = generator.generate_all_commands(
            modes=modes, temp_range=temp_range, fan_speeds=fan_speeds
        )

        # Count total commands
        total_commands = 1  # off command
        for mode_commands in commands.values():
            if isinstance(mode_commands, dict):
                for fan_commands in mode_commands.values():
                    if isinstance(fan_commands, dict):
                        total_commands += len(fan_commands)

        return GenerateResponse(
            success=True,
            manufacturer=request.manufacturer,
            protocol=request.protocol,
            totalCommands=total_commands,
            commands=commands,
        )

    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "INVALID_PARAMETERS",
                "message": "Invalid generation parameters",
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
