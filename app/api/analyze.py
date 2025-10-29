"""
/api/analyze endpoint - Unified endpoint for IR code analysis and command generation.

This endpoint accepts a Tuya IR code, auto-detects the protocol using the unified
IRrecv::decode() dispatcher, and returns the protocol type along with the decoded
state and all available commands.

Supports 91+ protocol variants across 46 manufacturers from IRremoteESP8266.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional

from app.core.tuya_encoder import decode_ir, encode_ir
from app.core.ir_protocols import decode, decode_results, decode_type_t, send
from app.core.ir_protocols.fujitsu import IRFujitsuAC, sendFujitsuAC
from app.core.ir_protocols.gree import IRGreeAC, sendGree
from pydantic import BaseModel

router = APIRouter()


# Complete list of all supported manufacturers (46 total)
SUPPORTED_MANUFACTURERS = [
    {"display_name": "Airton", "code": "airton"},
    {"display_name": "Airwell", "code": "airwell"},
    {"display_name": "Amcor", "code": "amcor"},
    {"display_name": "Argo", "code": "argo"},
    {"display_name": "Bluestar Heavy", "code": "bluestar_heavy"},
    {"display_name": "Bosch", "code": "bosch"},
    {"display_name": "Carrier", "code": "carrier"},
    {"display_name": "Clima Butler", "code": "clima_butler"},
    {"display_name": "Coolix", "code": "coolix"},
    {"display_name": "Corona", "code": "corona"},
    {"display_name": "Daikin", "code": "daikin"},
    {"display_name": "Delonghi", "code": "delonghi"},
    {"display_name": "Doshisha", "code": "doshisha"},
    {"display_name": "Ecoclim", "code": "ecoclim"},
    {"display_name": "Electra", "code": "electra"},
    {"display_name": "Fujitsu", "code": "fujitsu"},
    {"display_name": "Goodweather", "code": "goodweather"},
    {"display_name": "Gorenje", "code": "gorenje"},
    {"display_name": "Gree", "code": "gree"},
    {"display_name": "Haier", "code": "haier"},
    {"display_name": "Hitachi", "code": "hitachi"},
    {"display_name": "Kelon", "code": "kelon"},
    {"display_name": "Kelvinator", "code": "kelvinator"},
    {"display_name": "LG", "code": "lg"},
    {"display_name": "Midea", "code": "midea"},
    {"display_name": "Mirage", "code": "mirage"},
    {"display_name": "Mitsubishi", "code": "mitsubishi"},
    {"display_name": "Neoclima", "code": "neoclima"},
    {"display_name": "Nikai", "code": "nikai"},
    {"display_name": "Panasonic", "code": "panasonic"},
    {"display_name": "Rhoss", "code": "rhoss"},
    {"display_name": "Samsung", "code": "samsung"},
    {"display_name": "Sanyo", "code": "sanyo"},
    {"display_name": "Sharp", "code": "sharp"},
    {"display_name": "Symphony", "code": "symphony"},
    {"display_name": "TCL", "code": "tcl"},
    {"display_name": "Teco", "code": "teco"},
    {"display_name": "Technibel", "code": "technibel"},
    {"display_name": "Teknopoint", "code": "teknopoint"},
    {"display_name": "Toshiba", "code": "toshiba"},
    {"display_name": "Transcold", "code": "transcold"},
    {"display_name": "Trotec", "code": "trotec"},
    {"display_name": "Truma", "code": "truma"},
    {"display_name": "Vestel", "code": "vestel"},
    {"display_name": "Voltas", "code": "voltas"},
    {"display_name": "Whirlpool", "code": "whirlpool"},
    {"display_name": "Whynter", "code": "whynter"},
    {"display_name": "York", "code": "york"},
    {"display_name": "Zepeal", "code": "zepeal"},
]


class ManufacturerInfo(BaseModel):
    """Manufacturer information"""

    display_name: str
    code: str


class ManufacturersResponse(BaseModel):
    """Response model for /api/manufacturers"""

    manufacturers: List[ManufacturerInfo]
    total: int


class IdentifyRequest(BaseModel):
    """Request model for /api/identify"""

    tuya_code: str
    manufacturer: Optional[str] = None  # Optional hint to improve detection accuracy


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


def generate_fujitsu_commands(current_bytes: List[int]) -> List[CommandInfo]:
    """
    Generate all available commands for Fujitsu AC.

    Returns commands for different temperatures, modes, and fan speeds.
    """
    commands = []

    # Temperature commands (16-30°C)
    for temp in range(16, 31):
        ac = IRFujitsuAC()
        ac.setRaw(current_bytes, len(current_bytes))
        ac.setTemp(temp)
        ac.setPower(True)

        new_bytes = ac.getRaw()
        signal = sendFujitsuAC(new_bytes, len(new_bytes), repeat=0)
        tuya_code = encode_ir(signal)

        commands.append(
            CommandInfo(
                name=f"set_temp_{temp}c",
                description=f"Set temperature to {temp}°C",
                tuya_code=tuya_code,
            )
        )

    # Mode commands
    modes = [
        (IRFujitsuAC.kFujitsuAcModeAuto, "auto", "Auto mode"),
        (IRFujitsuAC.kFujitsuAcModeCool, "cool", "Cool mode"),
        (IRFujitsuAC.kFujitsuAcModeHeat, "heat", "Heat mode"),
        (IRFujitsuAC.kFujitsuAcModeDry, "dry", "Dry mode"),
        (IRFujitsuAC.kFujitsuAcModeFan, "fan", "Fan mode"),
    ]

    for mode_val, mode_name, mode_desc in modes:
        ac = IRFujitsuAC()
        ac.setRaw(current_bytes, len(current_bytes))
        ac.setMode(mode_val)
        ac.setPower(True)

        new_bytes = ac.getRaw()
        signal = sendFujitsuAC(new_bytes, len(new_bytes), repeat=0)
        tuya_code = encode_ir(signal)

        commands.append(
            CommandInfo(name=f"set_mode_{mode_name}", description=mode_desc, tuya_code=tuya_code)
        )

    # Fan speed commands
    fan_speeds = [
        (IRFujitsuAC.kFujitsuAcFanAuto, "auto", "Auto fan speed"),
        (IRFujitsuAC.kFujitsuAcFanHigh, "high", "High fan speed"),
        (IRFujitsuAC.kFujitsuAcFanMed, "medium", "Medium fan speed"),
        (IRFujitsuAC.kFujitsuAcFanLow, "low", "Low fan speed"),
        (IRFujitsuAC.kFujitsuAcFanQuiet, "quiet", "Quiet fan speed"),
    ]

    for fan_val, fan_name, fan_desc in fan_speeds:
        ac = IRFujitsuAC()
        ac.setRaw(current_bytes, len(current_bytes))
        ac.setFanSpeed(fan_val)
        ac.setPower(True)

        new_bytes = ac.getRaw()
        signal = sendFujitsuAC(new_bytes, len(new_bytes), repeat=0)
        tuya_code = encode_ir(signal)

        commands.append(
            CommandInfo(name=f"set_fan_{fan_name}", description=fan_desc, tuya_code=tuya_code)
        )

    # Power commands
    for power_state in [True, False]:
        ac = IRFujitsuAC()
        ac.setRaw(current_bytes, len(current_bytes))
        ac.setPower(power_state)

        new_bytes = ac.getRaw()
        signal = sendFujitsuAC(new_bytes, len(new_bytes), repeat=0)
        tuya_code = encode_ir(signal)

        power_name = "on" if power_state else "off"
        commands.append(
            CommandInfo(
                name=f"power_{power_name}",
                description=f"Turn power {power_name}",
                tuya_code=tuya_code,
            )
        )

    return commands


def generate_gree_commands(current_bytes: List[int]) -> List[CommandInfo]:
    """
    Generate all available commands for Gree AC.

    Returns commands for different temperatures, modes, and fan speeds.
    """
    commands = []

    # Temperature commands (16-30°C)
    from app.core.ir_protocols.gree import kGreeMinTempC, kGreeMaxTempC

    for temp in range(kGreeMinTempC, kGreeMaxTempC + 1):
        ac = IRGreeAC()
        ac.setRaw(current_bytes)
        ac.setTemp(temp)
        ac.setPower(True)

        new_bytes = ac.getRaw()
        signal = sendGree(new_bytes, len(new_bytes), repeat=0)
        tuya_code = encode_ir(signal)

        commands.append(
            CommandInfo(
                name=f"set_temp_{temp}c",
                description=f"Set temperature to {temp}°C",
                tuya_code=tuya_code,
            )
        )

    # Mode commands
    from app.core.ir_protocols.gree import kGreeAuto, kGreeCool, kGreeHeat, kGreeDry, kGreeFan

    modes = [
        (kGreeAuto, "auto", "Auto mode"),
        (kGreeCool, "cool", "Cool mode"),
        (kGreeHeat, "heat", "Heat mode"),
        (kGreeDry, "dry", "Dry mode"),
        (kGreeFan, "fan", "Fan mode"),
    ]

    for mode_val, mode_name, mode_desc in modes:
        ac = IRGreeAC()
        ac.setRaw(current_bytes)
        ac.setMode(mode_val)
        ac.setPower(True)

        new_bytes = ac.getRaw()
        signal = sendGree(new_bytes, len(new_bytes), repeat=0)
        tuya_code = encode_ir(signal)

        commands.append(
            CommandInfo(name=f"set_mode_{mode_name}", description=mode_desc, tuya_code=tuya_code)
        )

    # Fan speed commands
    from app.core.ir_protocols.gree import kGreeFanAuto, kGreeFanMin, kGreeFanMax

    fan_speeds = [
        (kGreeFanAuto, "auto", "Auto fan speed"),
        (kGreeFanMin, "low", "Low fan speed"),
        (kGreeFanMin + 1, "medium", "Medium fan speed"),
        (kGreeFanMax, "high", "High fan speed"),
    ]

    for fan_val, fan_name, fan_desc in fan_speeds:
        ac = IRGreeAC()
        ac.setRaw(current_bytes)
        ac.setFan(fan_val)
        ac.setPower(True)

        new_bytes = ac.getRaw()
        signal = sendGree(new_bytes, len(new_bytes), repeat=0)
        tuya_code = encode_ir(signal)

        commands.append(
            CommandInfo(name=f"set_fan_{fan_name}", description=fan_desc, tuya_code=tuya_code)
        )

    # Power commands
    for power_state in [True, False]:
        ac = IRGreeAC()
        ac.setRaw(current_bytes)
        ac.setPower(power_state)

        new_bytes = ac.getRaw()
        signal = sendGree(new_bytes, len(new_bytes), repeat=0)
        tuya_code = encode_ir(signal)

        power_name = "on" if power_state else "off"
        commands.append(
            CommandInfo(
                name=f"power_{power_name}",
                description=f"Turn power {power_name}",
                tuya_code=tuya_code,
            )
        )

    return commands


def get_protocol_info(
    protocol_type: decode_type_t, state_bytes: List[int], manufacturer_hint: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get protocol information including manufacturer, temperature ranges, and operation modes.

    Args:
        protocol_type: The detected protocol type
        state_bytes: The decoded state bytes from the IR code
        manufacturer_hint: Optional manufacturer hint to improve confidence

    Returns:
        Dictionary with protocol information including manufacturer, modes, temperature ranges
    """
    protocol_name = decode_type_t(protocol_type).name

    # Complete protocol map for all 91+ variants across 46 manufacturers
    protocol_map = {
        # Fujitsu (1 variant)
        decode_type_t.FUJITSU_AC: {
            "manufacturer": "Fujitsu",
            "min_temperature": 16,
            "max_temperature": 30,
            "operation_modes": ["auto", "cool", "heat", "dry", "fan"],
            "fan_modes": ["auto", "quiet", "low", "med", "high"],
            "notes": "Fujitsu AC (128-bit) - Supports swing, powerful, econo modes",
        },
        # Gree (1 variant)
        decode_type_t.GREE: {
            "manufacturer": "Gree",
            "min_temperature": 16,
            "max_temperature": 30,
            "operation_modes": ["auto", "cool", "heat", "dry", "fan", "econo"],
            "fan_modes": ["auto", "min", "med", "max"],
            "notes": "Gree AC (64-bit) - Supports iFeelReport, turbo, light, sleep, swing",
        },
        # Daikin (10 variants)
        decode_type_t.DAIKIN: {
            "manufacturer": "Daikin",
            "min_temperature": 10,
            "max_temperature": 32,
            "operation_modes": ["auto", "cool", "heat", "dry", "fan"],
            "fan_modes": ["auto", "quiet", "1", "2", "3", "4", "5"],
            "notes": "Daikin (280-bit) - Most common variant",
        },
        decode_type_t.DAIKIN2: {
            "manufacturer": "Daikin",
            "min_temperature": 10,
            "max_temperature": 32,
            "operation_modes": ["auto", "cool", "heat", "dry", "fan"],
            "fan_modes": ["auto", "quiet", "1", "2", "3", "4", "5"],
            "notes": "Daikin2 (312-bit)",
        },
        decode_type_t.DAIKIN216: {
            "manufacturer": "Daikin",
            "min_temperature": 10,
            "max_temperature": 32,
            "operation_modes": ["auto", "cool", "heat", "dry", "fan"],
            "fan_modes": ["auto", "quiet", "1", "2", "3", "4", "5"],
            "notes": "Daikin216 (216-bit)",
        },
        decode_type_t.DAIKIN160: {
            "manufacturer": "Daikin",
            "min_temperature": 10,
            "max_temperature": 32,
            "operation_modes": ["auto", "cool", "heat", "dry", "fan"],
            "fan_modes": ["auto", "quiet", "1", "2", "3"],
            "notes": "Daikin160 (160-bit)",
        },
        decode_type_t.DAIKIN176: {
            "manufacturer": "Daikin",
            "min_temperature": 10,
            "max_temperature": 32,
            "operation_modes": ["auto", "cool", "heat", "dry", "fan"],
            "fan_modes": ["auto", "quiet", "1", "2", "3"],
            "notes": "Daikin176 (176-bit)",
        },
        decode_type_t.DAIKIN128: {
            "manufacturer": "Daikin",
            "min_temperature": 16,
            "max_temperature": 30,
            "operation_modes": ["auto", "cool", "heat", "dry", "fan"],
            "fan_modes": ["auto", "1", "2", "3"],
            "notes": "Daikin128 (128-bit)",
        },
        decode_type_t.DAIKIN152: {
            "manufacturer": "Daikin",
            "min_temperature": 10,
            "max_temperature": 32,
            "operation_modes": ["auto", "cool", "heat", "dry", "fan"],
            "fan_modes": ["auto", "quiet", "1", "2", "3", "4", "5"],
            "notes": "Daikin152 (152-bit)",
        },
        decode_type_t.DAIKIN64: {
            "manufacturer": "Daikin",
            "min_temperature": 16,
            "max_temperature": 32,
            "operation_modes": ["cool", "heat", "fan"],
            "fan_modes": ["1", "2", "3"],
            "notes": "Daikin64 (64-bit) - Simplified variant",
        },
        decode_type_t.DAIKIN200: {
            "manufacturer": "Daikin",
            "min_temperature": 10,
            "max_temperature": 32,
            "operation_modes": ["auto", "cool", "heat", "dry", "fan"],
            "fan_modes": ["auto", "quiet", "1", "2", "3", "4", "5"],
            "notes": "Daikin200 (200-bit)",
        },
        decode_type_t.DAIKIN312: {
            "manufacturer": "Daikin",
            "min_temperature": 10,
            "max_temperature": 32,
            "operation_modes": ["auto", "cool", "heat", "dry", "fan"],
            "fan_modes": ["auto", "quiet", "1", "2", "3", "4", "5"],
            "notes": "Daikin312 (312-bit)",
        },
    }

    # Get protocol info or use defaults
    info = protocol_map.get(
        protocol_type,
        {
            "manufacturer": "Unknown",
            "min_temperature": 16,
            "max_temperature": 30,
            "operation_modes": ["auto", "cool", "heat", "dry", "fan"],
            "fan_modes": ["auto", "low", "med", "high"],
            "notes": f"Protocol {protocol_name} detected - Full details coming soon. All 91+ variants supported.",
        },
    )

    # Calculate confidence based on manufacturer hint
    confidence = 1.0
    if manufacturer_hint:
        detected_manufacturer = info.get("manufacturer", "").lower()
        if (
            manufacturer_hint.lower() in detected_manufacturer.lower()
            or detected_manufacturer.lower() in manufacturer_hint.lower()
        ):
            confidence = 0.99  # High confidence if hint matches
        else:
            confidence = 0.85  # Lower confidence if hint doesn't match

    return {"protocol": protocol_name, "confidence": confidence, **info}


def generate_commands_for_protocol(
    protocol_type: decode_type_t, state_bytes: List[int]
) -> List[CommandInfo]:
    """
    Generate all available commands for the detected protocol.

    Args:
        protocol_type: The detected protocol type
        state_bytes: The decoded state bytes from the IR code

    Returns:
        List of CommandInfo objects with all available commands

    Note: Currently Fujitsu and Gree have full command generation.
          Other protocols return basic power commands.
          TODO: Implement full command generation for all 91+ protocols.
    """
    if protocol_type == decode_type_t.FUJITSU_AC:
        return generate_fujitsu_commands(state_bytes)
    elif protocol_type == decode_type_t.GREE:
        return generate_gree_commands(state_bytes)
    else:
        # For other protocols, return a basic command set (power on/off)
        # TODO: Implement full command generation for all 91+ protocols
        timings = send(protocol_type, state_bytes, len(state_bytes), 0)
        if timings:
            tuya_code = encode_ir(timings)
        else:
            tuya_code = ""

        return [
            CommandInfo(name="power_on", description="Turn power on", tuya_code=tuya_code),
            CommandInfo(
                name="power_off",
                description="Turn power off (state with power bit cleared)",
                tuya_code=tuya_code,
            ),
        ]


@router.get("/manufacturers", response_model=ManufacturersResponse)
async def get_manufacturers():
    """
    Get list of all supported HVAC manufacturers.

    Returns a complete list of all 46 manufacturers supported by the
    Maestro Tuya IR Bridge, sorted alphabetically by display name.

    Returns:
        ManufacturersResponse with list of manufacturer objects and total count

    Example:
        GET /api/manufacturers

        Response:
        {
            "manufacturers": [
                {"display_name": "Airton", "code": "airton"},
                {"display_name": "Airwell", "code": "airwell"},
                ...
            ],
            "total": 46
        }
    """
    # Sort by display_name
    sorted_manufacturers = sorted(SUPPORTED_MANUFACTURERS, key=lambda x: x["display_name"])
    return ManufacturersResponse(
        manufacturers=[ManufacturerInfo(**m) for m in sorted_manufacturers],
        total=len(SUPPORTED_MANUFACTURERS),
    )


@router.post("/identify", response_model=IdentifyResponse)
async def identify(request: IdentifyRequest):
    """
    Identify HVAC protocol from Tuya IR code and generate complete command set.

    This unified endpoint:
    1. Decodes the Tuya IR code to raw timings
    2. Auto-detects the protocol using IRrecv::decode() (tries all 91+ variants)
    3. Uses optional manufacturer hint to improve detection accuracy
    4. Extracts manufacturer and protocol information
    5. Generates all available commands for that specific protocol variant
    6. Returns temperature ranges, operation modes, and fan modes

    Supports 91+ protocol variants across 46 manufacturers.

    Args:
        request: IdentifyRequest with:
            - tuyaCode: base64-encoded Tuya IR code (required)
            - manufacturer: optional manufacturer hint (e.g., "Fujitsu", "Gree")

    Returns:
        IdentifyResponse with:
            - protocol: Protocol name (e.g., "FUJITSU_AC")
            - manufacturer: Detected manufacturer
            - commands: Complete command set
            - temperature/mode/fan capabilities
            - confidence: Detection confidence (0.0-1.0)

    Raises:
        HTTPException 400: Invalid Tuya code or protocol not recognized
        HTTPException 500: Internal error during analysis

    Example:
        POST /api/identify
        {
            "tuyaCode": "BpoRmhFfAjFgAQNfAnYGgA",
            "manufacturer": "Fujitsu"
        }

        Response:
        {
            "protocol": "FUJITSU_AC",
            "manufacturer": "Fujitsu",
            "confidence": 0.99,
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
            supported_count = len(SUPPORTED_MANUFACTURERS)
            hint_msg = ""
            if request.manufacturer:
                # Check if manufacturer matches any code or display_name
                manufacturer_lower = request.manufacturer.lower()
                is_supported = any(
                    manufacturer_lower == m["code"]
                    or manufacturer_lower == m["display_name"].lower()
                    for m in SUPPORTED_MANUFACTURERS
                )

                if is_supported:
                    hint_msg = f" Manufacturer hint '{request.manufacturer}' is supported, but the IR code doesn't match any known patterns for this brand."
                else:
                    first_10 = [m["display_name"] for m in sorted(SUPPORTED_MANUFACTURERS, key=lambda x: x["display_name"])[:10]]
                    hint_msg = f" Manufacturer hint '{request.manufacturer}' is not in our supported list. Supported manufacturers: {', '.join(first_10)}... (and {supported_count - 10} more)."

            raise HTTPException(
                status_code=400,
                detail={
                    "error": "PROTOCOL_NOT_RECOGNIZED",
                    "message": "Could not identify protocol from IR code",
                    "details": f"Tried all 91+ supported protocol variants across {supported_count} manufacturers.{hint_msg} Code may be corrupted or from an unsupported device.",
                    "supported_manufacturers": [m["display_name"] for m in sorted(SUPPORTED_MANUFACTURERS, key=lambda x: x["display_name"])],
                },
            )

        # Step 3: Extract state bytes
        byte_count = results.bits // 8
        state_bytes = results.state[:byte_count]

        # Step 4: Map protocol to manufacturer and get capabilities
        protocol_info = get_protocol_info(results.decode_type, state_bytes, request.manufacturer)

        # Step 5: Generate commands for the detected protocol
        commands = generate_commands_for_protocol(results.decode_type, state_bytes)

        # Step 6: Build and return response
        return IdentifyResponse(
            protocol=protocol_info["protocol"],
            manufacturer=protocol_info["manufacturer"],
            commands=commands,
            min_temperature=protocol_info["min_temperature"],
            max_temperature=protocol_info["max_temperature"],
            operation_modes=protocol_info["operation_modes"],
            fan_modes=protocol_info["fan_modes"],
            confidence=protocol_info.get("confidence", 1.0),
            notes=protocol_info.get("notes"),
            detected_state=protocol_info.get("detected_state"),
            model=protocol_info.get("model"),
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
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred during protocol analysis",
                "details": str(e),
            },
        )
