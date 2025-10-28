"""IR Protocol implementations"""

# Import from ir_send (IRsend.cpp translations)
from app.core.ir_protocols.ir_send import (
    sendData,
    sendGeneric,
)

# Import from fujitsu (ir_Fujitsu.cpp translations)
from app.core.ir_protocols.fujitsu import (
    sendFujitsuAC,
)

# Import from ir_recv (IRrecv.cpp translations)
from app.core.ir_protocols.ir_recv import (
    matchMark,
    matchSpace,
    matchAtLeast,
    matchData,
    matchBytes,
    _matchGeneric,
    match_result_t,
    reverseBits,
    decode_results,
    decodeFujitsuAC,
    validate_timings,
    validate_fujitsu_timings,
)

__all__ = [
    # Encoding (from ir_send.py)
    'sendData',
    'sendGeneric',
    # Fujitsu-specific (from fujitsu.py)
    'sendFujitsuAC',
    # Decoding (from ir_recv.py)
    'matchMark',
    'matchSpace',
    'matchAtLeast',
    'matchData',
    'matchBytes',
    '_matchGeneric',
    'match_result_t',
    'reverseBits',
    'decode_results',
    'decodeFujitsuAC',
    'validate_timings',
    'validate_fujitsu_timings',
]
