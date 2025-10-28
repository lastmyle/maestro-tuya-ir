from app.core.ir_protocols.fujitsu import IRFujitsuAC, sendFujitsuAC
from app.core.ir_protocols.ir_recv import decode_results, decodeFujitsuAC, kFujitsuAcBits
from app.core.tuya_encoder import decode_ir, encode_ir
from tests.test_tuya_encoder_roundtrip import KNOWN_GOOD_CODES

import requests
import urllib.parse

def test_round_trip():
    original = KNOWN_GOOD_CODES["24C_High"]  # Example code for testing

    # Decode using EXACT C++ translation
    signal = decode_ir(original)

    # Use decodeFujitsuAC (EXACT C++ translation)
    results = decode_results()
    results.rawbuf = signal
    results.rawlen = len(signal)

    success = decodeFujitsuAC(results, offset=0, nbits=kFujitsuAcBits, strict=False)
    assert success, "decodeFujitsuAC should succeed"

    byte_count = results.bits // 8
    bytes = results.state[:byte_count]

    command = IRFujitsuAC()
    command.setRaw(bytes, len(bytes))
    command.setTemp(24)  # Example temperature
    command.setFanSpeed(3)
    command.setPower(True)

    # Re-encode using sendFujitsuAC (EXACT C++ translation)
    new_bytes = command.getRaw()
    new_signal = sendFujitsuAC(new_bytes, len(new_bytes), repeat=0)

    # encode_ir automatically removes trailing gap (> 8000µs)
    new_command = encode_ir(new_signal)

    print(f"Original: {original}")
    print(f"New: {new_command}")

    # Construct URL to send the new command to remote hub
    base_url = "https://cloud.hubitat.com/api/fa2f9b71-aa19-49c1-bfff-327f7da9037d/apps/4/devices/6/sendCode"
    access_token = "2e42137e-b1d4-4d29-8ef9-c098ca82304e"
    # URL-encode the command to handle special characters like / and +
    encoded_command = urllib.parse.quote(new_command, safe='')
    full_url = f"{base_url}/{encoded_command}?access_token={access_token}"

    print(f"\nSending to hub:")
    print(full_url)

    # Make API call to send the command
    response = requests.post(full_url, timeout=10)
    print(f"\nResponse status: {response.status_code}")
    print(f"Response body: {response.text}")
    response.raise_for_status()
    print("✓ Command sent successfully!")
 


def test_send_code():

    command = IRFujitsuAC()
    command.setTemp(24)  # Example temperature
    command.setFanSpeed(3)
    command.setPower(False)

    # Re-encode using sendFujitsuAC (EXACT C++ translation)
    new_bytes = command.getRaw()
    new_signal = sendFujitsuAC(new_bytes, len(new_bytes), repeat=0)

    # encode_ir automatically removes trailing gap (> 8000µs)
    new_command = encode_ir(new_signal)

    print(f"New: {new_command}")

    # Construct URL to send the new command to remote hub
    base_url = "https://cloud.hubitat.com/api/fa2f9b71-aa19-49c1-bfff-327f7da9037d/apps/4/devices/6/sendCode"
    access_token = "2e42137e-b1d4-4d29-8ef9-c098ca82304e"
    # URL-encode the command to handle special characters like / and +
    encoded_command = urllib.parse.quote(new_command, safe='')
    full_url = f"{base_url}/{encoded_command}?access_token={access_token}"

    print(f"\nSending to hub:")
    print(full_url)

    # Make API call to send the command
    response = requests.post(full_url, timeout=10)
    print(f"\nResponse status: {response.status_code}")
    print(f"Response body: {response.text}")
    response.raise_for_status()
    print("✓ Command sent successfully!")
 

