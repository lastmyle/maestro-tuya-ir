"""
/api/identify endpoint - Unified endpoint for IR code analysis and command generation.

This endpoint accepts a Tuya IR code, auto-detects the protocol using the unified
IRrecv::decode() dispatcher, and returns the protocol type along with the decoded
state and all available commands.

Supports 91+ protocol variants across 46 manufacturers from IRremoteESP8266.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional

from app.core.tuya_encoder import decode_ir
from app.core.ir_protocols import decode, decode_results, decode_type_t
from app.services import command_generator
from pydantic import BaseModel

router = APIRouter()


class IdentifyRequest(BaseModel):
    """Request model for /api/identify"""

    tuya_code: str


class CommandInfo(BaseModel):
    """Information about a single command"""

    name: str
    description: str
    tuya_code: str


class IdentifyResponse(BaseModel):
    """Response model for /api/identify"""

    protocol: str  # Protocol name (e.g., "FUJITSU_AC", "GREE", "DAIKIN")
    manufacturer: str  # Manufacturer name(s)
    commands: List[CommandInfo]  # Complete command set
    min_temperature: int  # Minimum temperature supported
    max_temperature: int  # Maximum temperature supported
    operation_modes: List[str]  # Available operation modes (cool, heat, dry, fan, auto)
    fan_modes: List[str]  # Available fan modes (auto, low, med, high, etc.)
    # Optional fields
    confidence: Optional[float] = None  # Confidence in protocol detection (0.0-1.0)
    notes: Optional[str] = None  # Additional notes about the protocol
    detected_state: Optional[Dict[str, Any]] = None  # Current state from the IR code
    model: Optional[str] = None  # Specific model if detected


@router.post("/identify", response_model=IdentifyResponse)
async def identify(request: IdentifyRequest):
    """
    Identify HVAC protocol from Tuya IR code and generate complete command set.

    This unified endpoint:
    1. Decodes the Tuya IR code to raw timings
    2. Auto-detects the protocol using IRrecv::decode() (tries all 91+ variants)
    3. Extracts manufacturer and protocol information
    4. Generates all available commands for that specific protocol variant
    5. Returns temperature ranges, operation modes, and fan modes

    Supports 91+ protocol variants across 46 manufacturers.

    Args:
        request: IdentifyRequest with:
            - tuyaCode: base64-encoded Tuya IR code (required)

    Returns:
        IdentifyResponse with:
            - protocol: Protocol name (e.g., "FUJITSU_AC")
            - manufacturer: Detected manufacturer
            - commands: Complete command set
            - temperature/mode/fan capabilities
            - confidence: Detection confidence (always 1.0)

    Raises:
        HTTPException 400: Invalid Tuya code or protocol not recognized
        HTTPException 500: Internal error during analysis

    Example:
        POST /api/identify
        {
            "tuyaCode": "BpoRmhFfAjFgAQNfAnYGgA"
        }

        Response:
        {
            "protocol": "FUJITSU_AC",
            "manufacturer": "Fujitsu",
            "confidence": 1.0,
            "commands": [...],
            "min_temperature": 16,
            "max_temperature": 30,
            ...
        }
    """
    try:
        # Step 1: Decode Tuya code to timings
        timings = decode_ir(request.tuya_code)

        # Step 2: Auto-detect protocol using unified IRrecv::decode() dispatcher
        results = decode_results()
        results.rawbuf = timings
        results.rawlen = len(timings)

        if not decode(results):
            # Provide helpful error message
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "PROTOCOL_NOT_RECOGNIZED",
                    "message": "Could not identify protocol from IR code",
                    "details": "Tried all 91+ supported protocol variants across 46 manufacturers. Code may be corrupted or from an unsupported device.",
                },
            )

        # Step 3: Extract state bytes
        byte_count = results.bits // 8
        state_bytes = results.state[:byte_count]

        # Step 4: Get protocol info and commands in one call
        result = command_generator.identify_protocol_and_generate_commands(
            results.decode_type, state_bytes
        )

        # Convert service CommandInfo to API CommandInfo
        commands = [
            CommandInfo(
                name=cmd.name,
                description=cmd.description,
                tuya_code=cmd.tuya_code,
            )
            for cmd in result["commands"]
        ]

        # Step 5: Build and return response
        return IdentifyResponse(
            protocol=result["protocol"],
            manufacturer=result["manufacturer"],
            commands=commands,
            min_temperature=result["min_temperature"],
            max_temperature=result["max_temperature"],
            operation_modes=result["operation_modes"],
            fan_modes=result["fan_modes"],
            confidence=result.get("confidence", 1.0),
            notes=result.get("notes"),
            detected_state=result.get("detected_state"),
            model=result.get("model"),
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_TUYA_CODE",
                "message": "Invalid Tuya IR code format",
                "details": str(e),
            },
        )
    except Exception as e:
        import traceback

        traceback.print_exc()  # Print to console for debugging
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during protocol analysis",
                "details": f"{type(e).__name__}: {str(e)}",
            },
        )
