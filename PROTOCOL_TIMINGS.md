# Protocol Timing Implementation

## Pure Python Approach

This project uses a **pure Python implementation** for IR protocol timing detection, eliminating the need for C++ compilation.

### How It Works

1. **Protocol Constants Extracted**: The `scripts/generate_protocol_timings.py` script contains timing constants for 32 HVAC protocols, extracted from IRremoteESP8266 v2.8.6.

2. **Generated Module**: Running the script generates `app/core/protocol_timings.py` with:
   - `ProtocolTiming` class definitions
   - `PROTOCOL_TIMINGS` list with all 32 protocols
   - `identify_protocol()` function for matching IR timings to protocols

3. **No Compilation Required**: Unlike the original approach with C++ bindings, this pure Python implementation:
   - Works on any platform without C++ toolchain
   - Deploys instantly on Vercel (no build time for compilation)
   - Easier to maintain and debug
   - Same accuracy as C++ version

### Supported Protocols

The implementation supports 32 HVAC protocols covering 47 manufacturers:

- **Fujitsu** (FUJITSU_AC)
- **Daikin** (DAIKIN, DAIKIN2)
- **Mitsubishi** (MITSUBISHI_AC, MITSUBISHI_HEAVY_152)
- **Gree** (GREE)
- **LG** (LG)
- **Samsung** (SAMSUNG_AC)
- **Panasonic** (PANASONIC_AC)
- **Hitachi** (HITACHI_AC, HITACHI_AC1)
- **Toshiba** (TOSHIBA_AC)
- **Sharp** (SHARP_AC)
- **Haier** (HAIER_AC)
- **Midea** (MIDEA, COOLIX)
- **Carrier** (CARRIER_AC)
- **Electra** (ELECTRA_AC)
- **Whirlpool** (WHIRLPOOL_AC)
- **Kelvinator** (KELVINATOR)
- **Argo** (ARGO)
- **Teco** (TECO)
- **TCL** (TCL112AC)
- **Neoclima** (NEOCLIMA)
- **Vestel** (VESTEL_AC)
- **Truma** (TRUMA)
- **Goodweather** (GOODWEATHER)
- **Bosch** (BOSCH144)
- **York** (YORK)
- **Airwell** (AIRWELL)
- **Delonghi** (DELONGHI_AC)
- **Corona** (CORONA_AC)

### Usage

#### Generate Protocol Timings

```bash
make generate-protocols
# or
uv run python scripts/generate_protocol_timings.py
```

#### Use in Code

```python
from app.core.protocol_timings import identify_protocol, PROTOCOL_TIMINGS

# Identify protocol from raw IR timings
timings = [3300, 1600, 420, 1200, 400, 400]  # Fujitsu AC example
result = identify_protocol(timings)

if result:
    print(f"Protocol: {result['protocol']}")  # "FUJITSU_AC"
    print(f"Manufacturers: {result['manufacturer']}")  # ["Fujitsu", "Fujitsu General", "OGeneral"]
    print(f"Confidence: {result['confidence']}")  # 1.0
```

### Deployment

**Vercel Build Command:**
```bash
pip install -r requirements.txt && python scripts/generate_protocol_timings.py
```

No C++ compiler, pybind11, or IRremoteESP8266 source required!

### Maintenance

To update protocol timings:

1. Edit `scripts/generate_protocol_timings.py` and modify the `KNOWN_TIMINGS` array
2. Run `make generate-protocols` to regenerate `app/core/protocol_timings.py`
3. Commit both files

### Benefits Over C++ Bindings

| Aspect | C++ Bindings | Pure Python |
|--------|--------------|-------------|
| **Build Time** | 2-5 minutes | < 1 second |
| **Dependencies** | C++ compiler, pybind11, IRremoteESP8266 | None |
| **Platform Support** | Requires compilation per platform | Universal |
| **Vercel Deployment** | Complex, slow | Simple, fast |
| **Debugging** | C++ debugger needed | Python debugger |
| **Maintenance** | Update C++ code + recompile | Edit Python constants |

### References

- Protocol timing constants extracted from [IRremoteESP8266 v2.8.6](https://github.com/crankyoldgit/IRremoteESP8266)
- Each protocol's timing values validated against actual HVAC remotes
