"""
/api/manufacturers endpoint - List manufacturers and generate commands from known good codes.

This endpoint provides two features:
1. GET /api/manufacturers - List all manufacturers with known good IR codes
2. POST /api/generate-from-manufacturer - Generate complete command set for a manufacturer

These endpoints enable the HVAC Setup Wizard to configure devices without requiring
manual IR code learning, by using pre-validated codes from the test_codes module.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional, Any, Dict
from pydantic import BaseModel

from app.core.ir_protocols.test_codes import ALL_KNOWN_GOOD_CODES, get_test_codes
from app.core.tuya_encoder import decode_ir
from app.core.ir_protocols import decode, decode_results
from app.services import command_generator

router = APIRouter()


class ManufacturersResponse(BaseModel):
    """Response model for /api/manufacturers"""

    manufacturers: List[str]


class ManufacturerRequest(BaseModel):
    """Request model for /api/generate-from-manufacturer"""

    manufacturer: str


class CommandInfo(BaseModel):
    """Information about a single command"""

    name: str
    description: str
    tuya_code: str


class GenerateResponse(BaseModel):
    """Response model for /api/generate-from-manufacturer"""

    protocol: str
    manufacturer: str
    commands: List[CommandInfo]
    min_temperature: int
    max_temperature: int
    operation_modes: List[str]
    fan_modes: List[str]
    confidence: Optional[float] = None
    notes: Optional[str] = None
    detected_state: Optional[Dict[str, Any]] = None
    model: Optional[str] = None


@router.get("/manufacturers", response_model=ManufacturersResponse)
async def list_manufacturers():
    """
    List all manufacturers with known good IR codes.

    Returns manufacturers that have at least one validated IR code in the
    test_codes database. These manufacturers can be used with the
    /api/generate-from-manufacturer endpoint to generate complete command sets
    without requiring manual IR code learning.

    Returns:
        ManufacturersResponse with:
            - manufacturers: List of manufacturer names with known good codes

    Example:
        GET /api/manufacturers

        Response:
        {
            "manufacturers": ["Fujitsu", "Mitsubishi", "Panasonic"]
        }
    """
    # Only return manufacturers with actual codes (non-empty dict)
    available = [
        name.title() for name, codes in ALL_KNOWN_GOOD_CODES.items() if codes
    ]
    return ManufacturersResponse(manufacturers=sorted(available))


@router.post("/generate-from-manufacturer", response_model=GenerateResponse)
async def generate_from_manufacturer(request: ManufacturerRequest):
    """
    Generate complete command set for a manufacturer using known good codes.

    This endpoint uses pre-validated IR codes to identify the protocol and
    generate a complete command set without requiring manual IR code learning.
    It's ideal for the HVAC Setup Wizard when the user knows their manufacturer.

    Args:
        request: ManufacturerRequest with:
            - manufacturer: Manufacturer name (case-insensitive, e.g., "Fujitsu")

    Returns:
        GenerateResponse with:
            - protocol: Protocol name (e.g., "FUJITSU_AC")
            - manufacturer: Manufacturer name
            - commands: Complete command set
            - temperature/mode/fan capabilities

    Raises:
        HTTPException 404: Manufacturer not found or no known codes available

    Example:
        POST /api/generate-from-manufacturer
        {
            "manufacturer": "Fujitsu"
        }

        Response:
        {
            "protocol": "FUJITSU_AC",
            "manufacturer": "Fujitsu",
            "commands": [...],
            "min_temperature": 16,
            "max_temperature": 30,
            ...
        }
    """
    # Get known good codes for this manufacturer
    manufacturer_key = request.manufacturer.lower()
    codes = get_test_codes(manufacturer_key)

    if not codes:
        raise HTTPException(
            status_code=404,
            detail=f"No known codes for manufacturer '{request.manufacturer}'. "
            f"Available manufacturers: {', '.join(m.title() for m, c in ALL_KNOWN_GOOD_CODES.items() if c)}",
        )

    # Use first available code - prefer OFF as it's usually most reliable
    test_code = codes.get("OFF") or list(codes.values())[0]

    # Decode the Tuya code to raw timings
    timings = decode_ir(test_code)

    # Use the unified IRrecv::decode() dispatcher to identify protocol
    results = decode_results()
    results.rawbuf = timings
    results.rawlen = len(timings)

    decode(results)

    # Extract state bytes
    byte_count = results.bits // 8
    state_bytes = results.state[:byte_count]

    # Generate full command set
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

    return GenerateResponse(
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
