"""IR Protocol implementations

This package contains Python translations of IRremoteESP8266 protocol implementations.

For protocol-specific constants and classes, import directly from the protocol module:
    from app.core.ir_protocols.fujitsu import IRFujitsuAC, sendFujitsuAC
    from app.core.ir_protocols.gree import IRGreeAC, sendGree, kGreeMinTempC

This package exposes the unified dispatch functions for convenience:
    - decode(): Auto-detect protocol from raw IR timings
    - send(): Encode protocol state to raw IR timings
    - decode_type_t: Protocol type enumeration
    - decode_results: Results object for decoding
"""

# Unified dispatcher functions (IRremoteESP8266 IRsend::send() and IRrecv::decode())
from app.core.ir_protocols.ir_dispatcher import (
    decode,
    send,
    decode_type_t,
)

# Decoder results structure
from app.core.ir_protocols.ir_recv import decode_results

__all__ = [
    "decode",
    "send",
    "decode_type_t",
    "decode_results",
]
