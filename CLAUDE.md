# Maestro Tuya IR Bridge - Project Guide

## Communication Style

**DO NOT APPEASE ME**

- Be direct and technical
- Don't validate or praise unnecessarily
- Focus on facts and problem-solving
- Disagree when you have better information
- Skip unnecessary politeness and get to the point
- No excessive superlatives or emotional validation

## Project Overview

The Maestro Tuya IR Bridge is a FastAPI service that translates, decodes, and generates complete IR command sets for Tuya-based HVAC devices. It allows Hubitat smart home devices to identify HVAC manufacturers from a single captured IR code and generate all possible commands for complete climate control.

## Key Features

- **Protocol Identification**: Detect manufacturer and protocol from Tuya IR codes using IRremoteESP8266 database
- **Command Generation**: Generate complete command sets (all temperatures, modes, fan speeds)
- **Tuya Format**: All codes are in Tuya format - ready for direct IR transmission
- **C++ Bindings**: Uses pybind11 bindings to IRremoteESP8266 for enhanced protocol detection

## Architecture

### Core Components

1. **API Endpoints** (`app/api/`)
   - `/api/identify` - Identify manufacturer/protocol from Tuya code
   - `/api/decode` - Decode Tuya IR code to raw timings
   - `/api/generate` - Generate complete command sets
   - `/api/encode` - Encode timings to Tuya format
   - `/api/health` - Service health check

2. **Core Logic** (`app/core/`)
   - `tuya.py` - Tuya format encoding/decoding with FastLZ compression
   - `protocols.py` - Protocol identification and management
   - `generator.py` - HVAC command set generation
   - `irremote_bindings.py` - C++ bindings to IRremoteESP8266
   - `irremote_esp8266_mapper.py` - Protocol timing database

3. **C++ Bindings** (`bindings/irremote/`)
   - `irremote_bindings.cpp` - pybind11 bindings for protocol detection
   - Uses IRremoteESP8266's timing database for 20+ HVAC protocols

### Workflow

```
User Captures 1 IR Code
         ↓
    /api/identify
         ↓
   Fujitsu AC detected
         ↓
   /api/generate
         ↓
  157 commands generated
         ↓
  Store on Hubitat
         ↓
Send to IR Blaster (no conversion!)
```

## Error Handling - CRITICAL

**NEVER SWALLOW ERRORS**

### Rules

1. **APIs**: Never catch and ignore exceptions. Always propagate or handle explicitly
2. **Services**: Never use bare `except:` or `except Exception: pass`
3. **Tests**: Never suppress errors - they indicate problems that must be fixed

### Good Practices

```python
# ✓ GOOD - Let errors propagate
def api_endpoint(data):
    result = process_data(data)
    return result

# ✓ GOOD - Handle specific errors explicitly
def api_endpoint(data):
    try:
        result = process_data(data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Database error")

# ✓ GOOD - Log and re-raise
def service_method():
    try:
        return risky_operation()
    except Exception as e:
        logger.error(f"Operation failed: {e}", exc_info=True)
        raise
```

### Bad Practices

```python
# ✗ BAD - Swallowing all errors
def api_endpoint(data):
    try:
        return process_data(data)
    except:
        return None

# ✗ BAD - Catching and ignoring
def service_method():
    try:
        risky_operation()
    except Exception:
        pass  # NEVER DO THIS

# ✗ BAD - Returning success despite error
def api_endpoint():
    try:
        process()
        return {"status": "success"}
    except:
        return {"status": "success"}  # LYING TO THE CLIENT
```

### Testing

Tests should NEVER suppress errors:

```python
# ✓ GOOD
def test_operation():
    result = dangerous_operation()
    assert result == expected

# ✗ BAD
def test_operation():
    try:
        dangerous_operation()
    except:
        pass  # Test passes even when it should fail!
```

### Development Principles

1. **Fail Fast**: Errors should be detected immediately
2. **Fail Loud**: Errors should be visible in logs and responses
3. **Fail Clearly**: Error messages should explain what went wrong
4. **Fail Safe**: Critical operations should be wrapped in transactions

### Exception Guidelines

- Use specific exception types
- Include context in error messages
- Log exceptions with full stack traces
- Return appropriate HTTP status codes
- Never return generic "success" responses when operations fail

## Development

### Setup

```bash
# Install dependencies (includes C++ build tools)
make install-dev

# Build C++ extensions (REQUIRED)
make build-ext

# Run tests
make test

# Lint code
make lint

# Format code
make format
```

### Testing

**49 total tests** organized by category:

1. **Unit Tests**
   - `test_tuya.py` - Tuya encoding/decoding
   - `test_protocols.py` - Protocol identification
   - `test_generator.py` - Command generation
   - `test_fastlz.py` - FastLZ compression

2. **Integration Tests**
   - `test_integration_api.py` - Full Hubitat workflow
   - `test_real_tuya_code.py` - Real Fujitsu IR codes
   - `test_second_tuya_code.py` - Additional Fujitsu codes

3. **Snapshot Tests** (`test_fujitsu_snapshots.py`)
   - Captures full API responses for manual testing
   - Use `pytest --snapshot-update` to regenerate
   - See `FUJITSU_TEST_CODES.md` for test codes

### Key Files

- `index.py` - FastAPI app entry point
- `setup.py` - C++ extension build configuration
- `pyproject.toml` - Python dependencies and config
- `vercel.json` - Vercel deployment (uses `uv`)
- `Makefile` - Development commands

## Testing with IR Blaster

1. Run `python generate_test_codes.py` to create test codes
2. Open `FUJITSU_TEST_CODES.md`
3. Copy Tuya codes and send to your IR blaster
4. Test different modes, temperatures, and fan speeds

Example codes are in:
- `FUJITSU_TEST_CODES.md` - Human-readable test commands
- `tests/__snapshots__/` - Syrupy snapshots with full command sets

## Important Notes

### Why Generated Codes Differ from Captured Codes

The original captured IR code will **NOT** match generated codes exactly. This is expected because:

1. **Real device timings** - Captured from actual HVAC with timing variations
2. **Idealized patterns** - Generator creates clean IR patterns from protocol specs
3. **Different states** - Captured code might be specific temp/mode not in generated set

**What matters:** Both decode to the same manufacturer/protocol (Fujitsu FUJITSU_AC)

See `test_fujitsu_roundtrip_validation` snapshot for proof:
- `original_code_matches_generated`: False ✅ (expected!)
- `workflow_validation.both_same_protocol`: True ✅ (what matters!)

### C++ Build Requirements

The C++ bindings are **REQUIRED** for the service to work. Without them, protocol detection falls back to basic header matching only.

Build on first install:
```bash
make install-dev  # Automatically builds extensions
```

Or manually:
```bash
python setup.py build_ext --inplace
```

## Deployment

### Vercel (Recommended)

Deploys automatically via GitHub. The `vercel.json` buildCommand:
```json
{
  "buildCommand": "pip install uv && uv sync --no-dev && uv run python setup.py build_ext --inplace"
}
```

This:
1. Installs `uv` for fast package management
2. Syncs dependencies from `uv.lock`
3. Builds C++ extensions

### Local Development

```bash
make dev  # Runs with auto-reload
```

## AWS SSO Authentication

### Setting Up AWS SSO for LastMyle Accounts

The project uses AWS SSO for secure access to LastMyle AWS accounts.

#### Initial Configuration

Add the following profiles to your `~/.aws/config` file:

```ini
[default]
region = us-west-2

[profile AdministratorAccess-440744230208]
sso_start_url = https://d-9067ed02ff.awsapps.com/start/#
sso_region = us-east-1
sso_account_id = 440744230208
sso_role_name = AdministratorAccess
region = us-west-2

[profile maestro-development]
sso_start_url = https://d-9067ed02ff.awsapps.com/start/#
sso_region = us-east-1
sso_account_id = 440744230208
sso_role_name = AdministratorAccess
region = us-west-2

[profile maestro-production]
sso_start_url = https://d-9067ed02ff.awsapps.com/start/#
sso_region = us-east-1
sso_account_id = 343218224546
sso_role_name = AdministratorAccess
region = us-west-2

[profile maestro-org]
sso_start_url = https://d-9067ed02ff.awsapps.com/start/#
sso_region = us-east-1
sso_account_id = 891377391463
sso_role_name = AdministratorAccess
region = us-west-2
```

#### Account Structure

The LastMyle AWS organization has three accounts:

- **maestro-development** (440744230208) - Development and testing environment
- **maestro-production** (343218224546) - Production environment
- **maestro-org** (891377391463) - Organization management account

All profiles use:
- SSO URL: https://d-9067ed02ff.awsapps.com/start/#
- SSO Region: us-east-1
- Default Region: us-west-2
- Role: AdministratorAccess

#### Logging In

```bash
# Login to development account
aws sso login --profile maestro-development

# Login to production account
aws sso login --profile maestro-production

# Login to organization account
aws sso login --profile maestro-org
```

This will:
1. Open your browser to https://d-9067ed02ff.awsapps.com/start/#
2. Prompt you to authorize the login
3. Cache credentials for 8 hours (default)

#### Using AWS CLI with SSO

```bash
# Set your profile for the current session
export AWS_PROFILE=maestro-development

# Or prefix individual commands
aws s3 ls --profile maestro-development

# For production
aws s3 ls --profile maestro-production
```

#### Troubleshooting SSO

**Session Expired**
```bash
# Re-login when credentials expire
aws sso login --profile maestro-development
```

**SSO Cache Issues**
```bash
# Clear SSO cache and re-login
rm -rf ~/.aws/sso/cache/
aws sso login --profile maestro-development
```

**Profile Not Found**
```bash
# Verify your AWS config
cat ~/.aws/config

# Ensure the maestro-* profiles are configured
```

#### Deployment with SSO

When deploying to AWS services (ECS, Lambda, etc.):

```bash
# Deploy to development
aws sso login --profile maestro-development
AWS_PROFILE=maestro-development make deploy

# Deploy to production
aws sso login --profile maestro-production
AWS_PROFILE=maestro-production make deploy-prod
```

#### Quick Reference

```bash
# Development workflow
aws sso login --profile maestro-development
export AWS_PROFILE=maestro-development
aws s3 ls
aws ecs list-clusters

# Production workflow
aws sso login --profile maestro-production
export AWS_PROFILE=maestro-production
aws s3 ls
aws ecs list-clusters
```

## Protocol Support

Currently supported manufacturers (via IRremoteESP8266):
- Carrier
- Daikin (multiple protocols)
- Fujitsu (FUJITSU_AC)
- Gree
- Hisense
- Hitachi
- Hyundai
- Mitsubishi

Each protocol includes:
- Header timing patterns
- Temperature ranges
- Mode support (cool/heat/dry/fan/auto)
- Fan speed options
- Special features (swing, quiet, powerful, etc.)

## Common Tasks

### Adding a New Protocol

1. Add to `PROTOCOLS` dict in `app/core/protocols.py`
2. Define header timings and capabilities
3. Update `get_supported_manufacturers()`
4. Add tests in `test_protocols.py`

### Updating Snapshots

```bash
pytest --snapshot-update
```

### Regenerating Test Codes

```bash
python generate_test_codes.py
# Creates FUJITSU_TEST_CODES.md
```

### Debugging Protocol Detection

```python
from app.core.protocols import identify_protocol
from app.core.tuya import decode_tuya_ir

code = "YOUR_TUYA_CODE_HERE"
timings = decode_tuya_ir(code)
result = identify_protocol(timings)
print(f"Manufacturer: {result['manufacturer']}")
print(f"Protocol: {result['protocol']}")
print(f"Confidence: {result['confidence']}")
```

## Performance

- **Fast protocol detection**: <10ms typical
- **Command generation**: 157 commands in ~20ms
- **Tuya encode/decode**: <1ms with FastLZ compression
- **Total workflow**: <50ms identify → generate

## CI/CD

GitHub Actions workflows:
- `.github/workflows/test.yml` - Run tests on push
- `.github/workflows/lint.yml` - Run linter
- Vercel auto-deploys on main branch

## Troubleshooting

### C++ Build Fails

Make sure you have C++ build tools:
```bash
# macOS
xcode-select --install

# Linux
sudo apt install build-essential python3-dev
```

### Protocol Not Identified

1. Check header timings: First 2 values should match known patterns
2. Try with manufacturer hint: `/api/identify` accepts `manufacturer` parameter
3. Check `tests/test_real_tuya_code.py` for similar examples

### Tests Failing

```bash
# Clean and rebuild
make clean
make install-dev
make test
```

## Contributing

1. Create feature branch
2. Add tests (maintain 100% coverage of new code)
3. Run `make lint` and `make test`
4. Update snapshots if API responses change
5. Submit PR

All commits include Claude Code attribution:
```
🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```
