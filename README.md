# Maestro Tuya HVAC IR Bridge

> The conductor for your climate control codes

Translate, decode, and generate complete IR command sets for Tuya-based HVAC devices. One learned code in, full temperature control out.

## Features

- **Decode Tuya IR Codes**: Convert Tuya Base64 format to raw IR timings
- **Identify Devices**: Detect manufacturer and protocol from a single IR code
- **Generate Command Sets**: Create complete HVAC control databases (245+ commands)
- **Encode Commands**: Generate individual IR codes for specific settings
- **IRremoteESP8266 Integration**: Enhanced protocol detection using timing database from the comprehensive IRremoteESP8266 library (47 HVAC manufacturers)
- **Multi-Manufacturer Support**: Fujitsu, Daikin, Mitsubishi, Gree, LG, Samsung, Panasonic, Hitachi, Toshiba, Sharp, Haier, Midea, and many more

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/yourusername/maestro-tuya-ir-bridge.git
cd maestro-tuya-ir-bridge

# Install dependencies
make install

# Or manually:
uv sync

# Run the development server
uv run uvicorn index:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/`.

## Deployment

### Deploy to AWS via Stacktape (Recommended)

Deploy as a serverless Lambda function on AWS with no VPC overhead.

**Prerequisites:**
```bash
# Install Stacktape CLI
npm install -g stacktape

# Authenticate with AWS
stacktape auth:aws --project-id maestro-ir-bridge
```

**Deploy:**
```bash
# Deploy to production
stacktape deploy --stage production --region us-east-1

# Your API will be live at:
# https://[your-api-id].execute-api.us-east-1.amazonaws.com
```

**Benefits:**
- $0/month cost (within AWS Lambda free tier for typical usage)
- No VPC overhead (serverless, pay-per-invocation)
- Consolidated with existing AWS/Stacktape infrastructure
- Auto-scaling with no server management

**Alternative: Vercel**

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/maestro-tuya-ir-bridge)

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions including Vercel, AWS ECS, GCP, and Azure.

## API Endpoints

### 1. Decode Tuya IR Code

**POST** `/api/decode`

Decode a Tuya Base64 IR code to raw timings and identify the protocol.

```bash
curl -X POST http://localhost:8000/api/decode \
  -H "Content-Type: application/json" \
  -d '{"tuyaCode": "Ed4MRQYFAkQBxAGIAcQBwATEAYAHQBMAiKABA..."}'
```

### 2. Identify Device

**POST** `/api/identify`

Identify manufacturer and capabilities from a single IR code.

```bash
curl -X POST http://localhost:8000/api/identify \
  -H "Content-Type: application/json" \
  -d '{"tuyaCode": "Ed4M...", "manufacturer": "Fujitsu"}'
```

### 3. Generate Complete Command Set

**POST** `/api/generate`

Generate all HVAC commands for a manufacturer/protocol.

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "manufacturer": "Fujitsu",
    "protocol": "fujitsu_ac",
    "filter": {
      "modes": ["cool", "heat"],
      "tempRange": [18, 26],
      "fanSpeeds": ["auto", "low", "high"]
    }
  }'
```

### 4. Encode Single Command

**POST** `/api/encode`

Generate a single HVAC command in Tuya format.

```bash
curl -X POST http://localhost:8000/api/encode \
  -H "Content-Type: application/json" \
  -d '{
    "manufacturer": "Fujitsu",
    "protocol": "fujitsu_ac",
    "command": {
      "power": "on",
      "mode": "cool",
      "temperature": 24,
      "fan": "auto",
      "swing": "off"
    }
  }'
```

### 5. Health Check

**GET** `/api/health`

Check service status and supported manufacturers.

```bash
curl http://localhost:8000/api/health
```

## Supported Manufacturers

Via **IRremoteESP8266 Protocol Database** (47 manufacturers, 32 protocols):
- **Fujitsu** (FUJITSU_AC, FUJITSU_AC264) - Full support with extended features
- **Daikin** (DAIKIN, DAIKIN2) - Including Econo and Powerful modes
- **Mitsubishi** (MITSUBISHI_AC, MITSUBISHI_HEAVY_152) - Standard HVAC controls
- **Gree** - With Turbo mode support
- **LG** - Including General Electric variants
- **Samsung** - AR series support
- **Panasonic** - CS series support
- **Hitachi** (HITACHI_AC, HITACHI_AC1) - Multiple protocol variants
- **Toshiba** / **Carrier** - RAS series
- **Sharp** - CRMC-A series
- **Haier** / **Daichi** - HSU series
- **Midea** / **Comfee** / **Electrolux** / **Keystone** / **Trotec** - MWMA series
- **Coolix** (Midea, Tokio, Airwell, Beko, Bosch) - Multi-brand protocol
- **Electra** / **AEG** / **AUX** / **Frigidaire** - YKR series
- **Whirlpool** - SPIS series
- And many more...

## Development

### Protocol Database

The project uses a generated Python module ([app/core/protocol_timings.py](app/core/protocol_timings.py)) containing timing constants from IRremoteESP8266 v2.8.6.

**Regenerating Protocol Timings:**
```bash
# Regenerate protocol_timings.py from hardcoded constants
python scripts/generate_protocol_timings.py
```

**Using Protocol Detection:**
```python
from app.core.protocol_timings import identify_protocol, get_supported_manufacturers

# Identify protocol from timings
timings = [3294, 1605, 420, 1200, ...]
result = identify_protocol(timings)
print(f"Manufacturer: {result['manufacturer']}")
print(f"Protocol: {result['protocol']}")
print(f"Confidence: {result['confidence']}")

# Get all supported manufacturers
manufacturers = get_supported_manufacturers()
print(f"Supported: {len(manufacturers)} manufacturers")
```

The protocol database provides:
- **32 HVAC protocols** with accurate timing definitions
- **47 manufacturer variants** (many brands share protocols)
- **Pure Python** implementation (no C++ compilation required)
- **Generated from IRremoteESP8266 v2.8.6** timing constants

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app tests/

# Run specific test file
uv run pytest tests/test_tuya.py
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Fix linting issues
uv run ruff check --fix .
```

### Adding Dependencies

```bash
# Add a runtime dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Update all dependencies
uv lock --upgrade
```

## CI/CD Pipeline

### Automated Checks

Every pull request and push triggers automated checks:

- ✅ **Tests** - Run all pytest tests
- ✅ **Lint** - Code quality checks with ruff
- ✅ **Lint PR** - Validates conventional commits format
- ✅ **Deployment Gate** - Blocks deployment until all checks pass

### Branch Protection

The `main` branch is protected with the following rules:

1. **Tests** must pass (pytest)
2. **Lint** must pass (ruff check + format)
3. **Lint PR** must pass (conventional commits)
4. **Deployment Gate** waits for all checks
5. **Code Owner Review** - @rhys-lastmyle must approve PRs
6. **Strict Status Checks** - Branches must be up to date before merging

Force pushes and branch deletion are disabled.

### Conventional Commits

All PR titles must follow the format: `<type>[scope]: <description>`

**Examples:**
- `feat: add Samsung AC protocol support`
- `fix(api): correct Fujitsu timing detection`
- `docs: update deployment guide`
- `test: add integration tests for Tuya codes`

See [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md) for contribution guidelines.

## Project Structure

```
maestro-tuya-ir-bridge/
├── app/
│   ├── api/               # API endpoints
│   │   ├── decode.py
│   │   ├── identify.py
│   │   ├── generate.py
│   │   ├── encode.py
│   │   └── health.py
│   ├── core/              # Core functionality
│   │   ├── fastlz.py           # FastLZ compression
│   │   ├── tuya.py             # Tuya format conversion
│   │   ├── protocol_timings.py # Protocol database (generated)
│   │   └── generator.py        # HVAC code generation
│   └── models/            # Pydantic models
│       ├── request.py
│       └── response.py
├── tests/                 # Test suite
├── data/                  # Sample data
├── index.py              # FastAPI application
├── pyproject.toml        # Project dependencies
├── uv.lock              # Locked dependencies
└── Dockerfile           # Docker configuration
```

## Technical Details

### Tuya IR Format

Tuya IR codes use a multi-step encoding process:

1. Raw IR timings (microseconds) → 16-bit little-endian integers
2. Binary data → FastLZ compression
3. Compressed bytes → Base64 encoding

This service handles the complete encoding/decoding pipeline.

### Protocol Detection

The service identifies HVAC protocols by analyzing IR timing patterns, specifically the header timing (mark/space microsecond values). Each manufacturer has distinct timing signatures.

### Code Generation

IR codes are generated based on protocol-specific timing templates. The generator creates valid timing patterns for all combinations of:

- Modes: cool, heat, dry, fan, auto
- Temperatures: 16-30°C (range varies by manufacturer)
- Fan speeds: auto, low, medium, high
- Additional features: swing, quiet, powerful, etc.

## Integration Example

### Hubitat Integration

```groovy
def identifyDevice(tuyaCode) {
    def params = [
        uri: "http://maestro-bridge:8000/api/identify",
        contentType: "application/json",
        body: [tuyaCode: tuyaCode, manufacturer: "Fujitsu"]
    ]

    httpPost(params) { resp ->
        def manufacturer = resp.data.manufacturer
        def protocol = resp.data.protocol

        // Generate all commands
        generateCommands(manufacturer, protocol)
    }
}
```

## Environment Variables

```bash
# Optional rate limiting
RATE_LIMIT_PER_MINUTE=100

# CORS configuration
ALLOWED_ORIGINS=*

# Optional Redis for caching
REDIS_URL=redis://localhost:6379
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file

## Acknowledgments

- [FastLZ](https://github.com/ariya/FastLZ) - Compression algorithm
- [IRremoteESP8266](https://github.com/crankyoldgit/IRremoteESP8266) - IR protocol reference
- Tuya IR format decoder [gist](https://gist.github.com/mildsunrise/1d576669b63a260d2cff35fda63ec0b5)

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/maestro-tuya-ir-bridge/issues
- Documentation: http://localhost:8000/ (when running)
