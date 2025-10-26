# 🎼 Maestro Tuya HVAC IR Bridge

> The conductor for your climate control codes

Translate, decode, and generate complete IR command sets for Tuya-based HVAC devices. One learned code in, full temperature control out.

## Project Overview

Build a FastAPI-based web service that translates between Tuya IR format and standard IR protocols, with the ability to generate complete HVAC command sets for any supported manufacturer based on a single learned IR code.

## Quick Start

### Prerequisites
- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/yourusername/maestro-tuya-ir-bridge.git
cd maestro-tuya-ir-bridge

# Install dependencies
uv sync

# Run the development server
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app tests/
```

### Development

```bash
# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Update dependencies
uv lock --upgrade

# Format and lint code
uv run ruff check .
uv run ruff format .
```

## Core Functionality

### 1. Decode Tuya IR Codes
- Accept Tuya format Base64 IR codes
- Decode to raw IR timing sequences
- Identify HVAC protocol and parameters (temp, mode, fan, etc.)

### 2. Detect Device from Single Code
- Analyze a single learned Tuya IR code
- Match against known HVAC protocols (Fujitsu, Daikin, Mitsubishi, etc.)
- Return manufacturer, model family, and detected settings

### 3. Generate Complete Command Sets
- Given manufacturer and optional model
- Generate ALL supported commands in Tuya format
- Return comprehensive database of temp/mode/fan combinations

---

## Technical Stack

### Required Libraries

**Note:** This project uses `uv` for dependency management. Dependencies are defined in `pyproject.toml`.

```toml
[project]
name = "maestro-tuya-ir-bridge"
version = "1.0.0"
description = "Translate, decode, and generate complete IR command sets for Tuya-based HVAC devices"
requires-python = ">=3.14"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",
    "hvac-ir>=0.1.0",  # https://github.com/shprota/hvac_ir
    # Supports: Fujitsu, Daikin, Mitsubishi, Gree, Carrier, Hisense, Hitachi, Hyundai
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "httpx>=0.25.0",  # For testing FastAPI
    "ruff>=0.1.0",    # Linting and formatting
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Note on FastLZ:** We'll implement the FastLZ decoder/encoder based on: https://gist.github.com/mildsunrise/1d576669b63a260d2cff35fda63ec0b5

---

## Tuya IR Code Format Specification

### Encoding Process
```
Raw IR timings (microseconds: [100, 200, 150, ...])
    ↓ Pack as 16-bit little-endian integers
Raw binary bytes
    ↓ FastLZ compression
Compressed bytes
    ↓ Base64 encoding
Tuya IR code (e.g., "Ed4M...")
```

### Decoding Process
```
Tuya IR code (Base64 string)
    ↓ Base64 decode
Compressed bytes
    ↓ FastLZ decompression
Raw binary bytes
    ↓ Unpack 16-bit little-endian integers
Raw IR timings (microseconds array)
```

---

## API Endpoints

### 1. Decode Tuya IR Code

**Endpoint:** `POST /api/decode`

**Request:**
```json
{
  "tuyaCode": "Ed4MRQYFAkQBxAGIAcQBwATEAYAHQBMAiKABA8QBwASAA0ALQAMGRAHEAcAEiCADA..."
}
```

**Response:**
```json
{
  "success": true,
  "timings": [9000, 4500, 600, 540, ...],
  "protocol": {
    "name": "fujitsu_ac",
    "manufacturer": "Fujitsu",
    "confidence": 0.95
  },
  "state": {
    "power": "on",
    "mode": "cool",
    "temperature": 24,
    "fan": "auto",
    "swing": "off"
  }
}
```

---

### 2. Identify Device from Code

**Endpoint:** `POST /api/identify`

**Request:**
```json
{
  "tuyaCode": "Ed4M...",
  "manufacturer": "Fujitsu"  // Optional hint
}
```

**Response:**
```json
{
  "success": true,
  "manufacturer": "Fujitsu",
  "protocol": "fujitsu_ac",
  "modelFamily": "AWYZ",
  "capabilities": {
    "modes": ["cool", "heat", "dry", "fan", "auto"],
    "fanSpeeds": ["low", "medium", "high", "auto"],
    "tempRange": {
      "min": 16,
      "max": 30,
      "unit": "celsius"
    },
    "features": ["swing", "quiet", "powerful"]
  },
  "detectedState": {
    "mode": "cool",
    "temperature": 24,
    "fan": "auto"
  }
}
```

---

### 3. Generate Complete Command Set

**Endpoint:** `POST /api/generate`

**Request:**
```json
{
  "manufacturer": "Fujitsu",
  "protocol": "fujitsu_ac",
  "filter": {
    "modes": ["cool", "heat"],
    "tempRange": [18, 26],
    "fanSpeeds": ["auto", "low", "high"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "manufacturer": "Fujitsu",
  "protocol": "fujitsu_ac",
  "totalCommands": 245,
  "commands": {
    "off": "B9wMWQalAYQBgAMDzQSlAUAL...",
    "cool": {
      "auto": {
        "16": "Ed4M...",
        "17": "Fx3N...",
        "18": "Gy2L...",
        "30": "Hz1K..."
      },
      "low": { },
      "medium": { },
      "high": { }
    },
    "heat": { },
    "dry": { },
    "fan": { }
  }
}
```

---

### 4. Encode Single Command

**Endpoint:** `POST /api/encode`

**Request:**
```json
{
  "manufacturer": "Fujitsu",
  "protocol": "fujitsu_ac",
  "command": {
    "power": "on",
    "mode": "cool",
    "temperature": 24,
    "fan": "auto",
    "swing": "off"
  }
}
```

**Response:**
```json
{
  "success": true,
  "tuyaCode": "Ed4MRQYFAkQBxAGIAcQBwATEAYAHQBMAiKABA...",
  "timings": [9000, 4500, 600, ...],
  "timingsLength": 347
}
```

---

### 5. Health Check

**Endpoint:** `GET /api/health`

**Response:**
```json
{
  "status": "ok",
  "supportedManufacturers": [
    "Fujitsu", "Daikin", "Mitsubishi", "Gree",
    "Carrier", "Hisense", "Hitachi", "Hyundai"
  ],
  "version": "1.0.0"
}
```

---

## Implementation Details

### 1. FastLZ Compression Implementation

Reference the Python implementation from:
https://gist.github.com/mildsunrise/1d576669b63a260d2cff35fda63ec0b5

```python
def fastlz_decompress(data: bytes) -> bytes:
    """
    Decompress FastLZ compressed data.
    Tuya uses FastLZ for IR code compression.
    """
    # Implement based on gist reference
    pass

def fastlz_compress(data: bytes) -> bytes:
    """
    Compress data using FastLZ algorithm.
    Tuya uses FastLZ for IR code compression.
    """
    # Implement based on gist reference
    pass
```

---

### 2. Tuya Format Conversion

```python
import struct
import base64

def decode_tuya_ir(tuya_code: str) -> list[int]:
    """
    Convert Tuya Base64 IR code to raw timing array.

    Args:
        tuya_code: Base64 encoded Tuya IR code

    Returns:
        List of microsecond timings [9000, 4500, 600, ...]
    """
    # 1. Base64 decode
    compressed = base64.b64decode(tuya_code)

    # 2. FastLZ decompress
    raw_bytes = fastlz_decompress(compressed)

    # 3. Unpack 16-bit little-endian integers
    timings = []
    for i in range(0, len(raw_bytes), 2):
        timing = struct.unpack('<H', raw_bytes[i:i+2])[0]
        timings.append(timing)

    return timings

def encode_tuya_ir(timings: list[int]) -> str:
    """
    Convert raw timing array to Tuya Base64 IR code.

    Args:
        timings: List of microsecond timings

    Returns:
        Base64 encoded Tuya IR code
    """
    # 1. Pack as 16-bit little-endian integers
    raw_bytes = b''
    for timing in timings:
        raw_bytes += struct.pack('<H', timing)

    # 2. FastLZ compress
    compressed = fastlz_compress(raw_bytes)

    # 3. Base64 encode
    tuya_code = base64.b64encode(compressed).decode('ascii')

    return tuya_code
```

---

### 3. HVAC Code Generation

```python
import hvac_ir

def generate_fujitsu_command(
    mode: str,
    temperature: int,
    fan: str,
    power: str = "on"
) -> str:
    """
    Generate Fujitsu HVAC command in Tuya format.

    Args:
        mode: "cool", "heat", "dry", "fan", "auto"
        temperature: 16-30 (Celsius)
        fan: "low", "medium", "high", "auto"
        power: "on" or "off"

    Returns:
        Tuya Base64 IR code
    """
    sender = hvac_ir.get_sender('fujitsu')
    ac = sender()

    # Map string parameters to hvac_ir constants
    power_flag = sender.POWER_ON if power == "on" else sender.POWER_OFF
    mode_flag = getattr(sender, f'MODE_{mode.upper()}')
    fan_flag = getattr(sender, f'FAN_{fan.upper()}')

    # Generate IR timings
    ac.send(
        power_flag,
        mode_flag,
        fan_flag,
        temperature,
        sender.VDIR_SWING_DOWN,
        sender.HDIR_SWING,
        False
    )

    timings = ac.get_durations()

    # Convert to Tuya format
    return encode_tuya_ir(timings)
```

---

### 4. Protocol Detection

```python
def identify_protocol(timings: list[int]) -> dict:
    """
    Identify HVAC protocol from raw IR timings.

    Uses timing pattern analysis to match against known protocols.

    Args:
        timings: Raw microsecond timing array

    Returns:
        {
            "protocol": "fujitsu_ac",
            "manufacturer": "Fujitsu",
            "confidence": 0.95
        }
    """
    # Check header timing patterns for each protocol
    # Fujitsu: typically starts with [9000, 4500] or similar
    # Daikin: different header pattern
    # etc.

    protocols = {
        'fujitsu': {
            'header': (9000, 4500),
            'tolerance': 200
        },
        'daikin': {
            'header': (3500, 1728),
            'tolerance': 200
        }
        # Add more protocols
    }

    # Pattern matching logic
    pass
```

---

## Error Handling

All endpoints should handle errors gracefully:

### Bad Request (400)
```json
{
  "success": false,
  "error": "INVALID_TUYA_CODE",
  "message": "Invalid Base64 encoding in Tuya IR code",
  "details": "..."
}
```

### Not Found (404)
```json
{
  "success": false,
  "error": "PROTOCOL_NOT_FOUND",
  "message": "Could not identify IR protocol from provided code",
  "suggestions": ["Try providing manufacturer hint", "Ensure code is complete"]
}
```

### Unprocessable Entity (422)
```json
{
  "success": false,
  "error": "UNSUPPORTED_MANUFACTURER",
  "message": "Manufacturer 'XYZ' not supported",
  "supportedManufacturers": ["Fujitsu", "Daikin", ...]
}
```

---

## Example Usage Flow

### Hubitat Wizard Integration

```groovy
// In hvac-setup-app.groovy

def codeLearnedHandler(evt) {
    def tuyaCode = evt.value

    // Step 1: Identify device
    def identifyUrl = "https://your-service.com/api/identify"
    httpPost(uri: identifyUrl,
             body: [tuyaCode: tuyaCode, manufacturer: hvacManufacturer]) { resp ->

        def manufacturer = resp.data.manufacturer
        def protocol = resp.data.protocol
        def capabilities = resp.data.capabilities

        // Step 2: Generate complete command set
        def generateUrl = "https://your-service.com/api/generate"
        httpPost(uri: generateUrl,
                 body: [manufacturer: manufacturer, protocol: protocol]) { genResp ->

            def commands = genResp.data.commands

            // Step 3: Save to driver
            irDevice.setHvacConfig([
                manufacturer: manufacturer,
                protocol: protocol,
                commands: commands,
                offCommand: commands.off
            ])

            log.info "✅ Generated ${genResp.data.totalCommands} commands!"
        }
    }
}
```

---

## Testing Requirements

### Unit Tests
- Test FastLZ compression/decompression round-trip
- Test Tuya encoding/decoding with known codes
- Test each supported manufacturer

### Integration Tests
- Decode real Tuya codes captured from devices
- Generate commands and verify they match learned codes
- Test API endpoints with various inputs

### Test Data

Include sample Tuya IR codes for each supported manufacturer:

```python
SAMPLE_CODES = {
    "fujitsu_cool_24": "Ed4MRQYFAkQBxAGIAcQBwATEAYAHQBMAiKABA...",
    "fujitsu_heat_20": "B9wMWQalAYQBgAMDzQSlAUAL...",
    "daikin_cool_22": "Fx3N...",
    # etc.
}
```

---

## Deployment Considerations

### Environment Variables
```bash
# Optional rate limiting
RATE_LIMIT_PER_MINUTE=100

# Optional caching
REDIS_URL=redis://localhost:6379

# CORS for Hubitat access
ALLOWED_ORIGINS=*
```

### Docker Support

Provide Dockerfile for easy deployment:

```dockerfile
FROM public.ecr.aws/docker/library/python:3.14.0-alpine

WORKDIR /app

# Install system dependencies for building Python packages
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    curl

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"
ENV UV_SYSTEM_PYTHON=1

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev || uv sync --no-dev

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run with uv
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Project Structure

```
maestro-tuya-hvac-ir-bridge/
├── README.md
├── pyproject.toml               # Project metadata and dependencies
├── uv.lock                      # Locked dependencies (managed by uv)
├── .python-version              # Python version (3.14)
├── Dockerfile
├── .gitignore
├── main.py                      # FastAPI app entry point
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── decode.py           # /api/decode endpoint
│   │   ├── identify.py         # /api/identify endpoint
│   │   ├── generate.py         # /api/generate endpoint
│   │   ├── encode.py           # /api/encode endpoint
│   │   └── health.py           # /api/health endpoint
│   ├── core/
│   │   ├── __init__.py
│   │   ├── tuya.py             # Tuya format conversion
│   │   ├── fastlz.py           # FastLZ compression
│   │   ├── protocols.py        # Protocol detection
│   │   └── generator.py        # HVAC code generation
│   └── models/
│       ├── __init__.py
│       ├── request.py          # Pydantic request models
│       └── response.py         # Pydantic response models
├── tests/
│   ├── __init__.py
│   ├── test_tuya.py
│   ├── test_fastlz.py
│   ├── test_protocols.py
│   ├── test_generator.py
│   └── test_api.py
└── data/
    └── sample_codes.json       # Test data
```

---

## Stretch Goals (Optional)

1. **Learning Mode**: Accept multiple Tuya codes to improve detection accuracy
2. **Custom Protocols**: Allow uploading custom protocol definitions
3. **Caching**: Cache generated command sets to improve performance
4. **Webhook Support**: Notify Hubitat when generation is complete
5. **Web UI**: Simple interface for testing codes
6. **Database**: Store learned codes and protocol fingerprints

---

## Success Criteria

- ✅ Decode Tuya IR codes to raw timings
- ✅ Identify manufacturer from single code
- ✅ Generate complete Fujitsu command set (245+ commands)
- ✅ Round-trip: decode → encode produces identical code
- ✅ API response time < 500ms for generation endpoint
- ✅ Support at least 5 manufacturers (Fujitsu, Daikin, Mitsubishi, Gree, Carrier)

---

## Timeline Estimate

- FastLZ implementation: 4-6 hours
- Tuya format conversion: 2-3 hours
- API endpoints: 3-4 hours
- hvac_ir integration: 2-3 hours
- Testing: 3-4 hours
- Documentation: 2 hours

**Total: 16-22 hours**

---

## Resources

### Key References

1. **Tuya IR Format Decoder** (Python)
   - https://gist.github.com/mildsunrise/1d576669b63a260d2cff35fda63ec0b5

2. **hvac_ir Library** (Python HVAC code generator)
   - https://github.com/shprota/hvac_ir

3. **IRremoteESP8266** (C++ reference implementation)
   - https://github.com/crankyoldgit/IRremoteESP8266

4. **FastLZ Algorithm**
   - https://github.com/ariya/FastLZ

### Example Tuya IR Codes

Captured from Fujitsu 24°C Cool:
```
Ed4MRQYFAkQBxAGIAcQBwATEAYAHQBMAiKABA8QBwASAA0ALQAMGRAHEAcAEiCADA8QBiAGAA0ATgAvAAUAPQAFAB4ADAsQBiGABQDfAL8AHAIhgAQDEIAEBiAHgAR8BiAFAD0ABQBMBwARAB0ADQAtAA0ALQAMBxAHARwjABIgBiAHEAYhgAUAH4AcDAYgBQCNAAwGIAYAbQAsCxAGIoAEBxAFAS0ADQAsDwATEAcALQA8AiKABwAlABwHEAYAhQAECxAGIYAFAB+ADA4ABQBGAAQDEIAEBRAFBZ0AHAsQBiCABgAUBiAGAB0AFAcQBgBsCxAGIYAHAB0ABAcQB4BMbQLcAiKABAcAE4AUDQAELwATEAYgBxAGIAYgB
```

---

## License

MIT License - see LICENSE file

---

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

---

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/maestro-tuya-hvac-ir-bridge/issues
- Documentation: (coming soon)
