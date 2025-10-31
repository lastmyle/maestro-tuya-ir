from app.core.ir_protocols.ir_dispatcher import decode
from app.core.ir_protocols.ir_recv import decode_results
from app.core.ir_protocols.test_codes import PANASONIC_KNOWN_GOOD_CODES
from app.core.tuya_encoder import decode_ir
from app.services import command_generator
from app.services.command_generator import generate_commands


def test_identify_protocol_and_generate_commands():
    # Step 1: Decode Tuya code to timings
    timings = decode_ir(PANASONIC_KNOWN_GOOD_CODES["ON"])

    # Step 2: Auto-detect protocol using unified IRrecv::decode() dispatcher
    results = decode_results()
    results.rawbuf = timings
    results.rawlen = len(timings)

    decode(results)

    # Step 3: Extract state bytes
    byte_count = results.bits // 8
    state_bytes = results.state[:byte_count]

    # Step 4: Get protocol info and commands in one call
    result = command_generator.identify_protocol_and_generate_commands(
        results.decode_type, state_bytes
    )
