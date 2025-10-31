from app.core.ir_protocols.fujitsu import IRFujitsuAC, sendFujitsuAC
from app.core.ir_protocols.ir_recv import decode_results, decodeFujitsuAC, kFujitsuAcBits
from app.core.tuya_encoder import decode_ir, encode_ir
from tests.test_tuya_encoder_roundtrip import KNOWN_GOOD_CODES
from app.settings import settings

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
    new_signal = sendFujitsuAC(new_bytes, len(new_bytes))

    # encode_ir automatically removes trailing gap (> 8000µs)
    new_command = encode_ir(new_signal)

    print(f"Original: {original}")
    print(f"New: {new_command}")

    # Construct URL to send the new command to remote hub (from settings)
    base_url = f"https://cloud.hubitat.com/api/{settings.hubitat.hub_id}/apps/{settings.hubitat.api_app_id}/devices/{settings.hubitat.device_id}/sendCode"
    # URL-encode the command to handle special characters like / and +
    encoded_command = urllib.parse.quote(new_command, safe="")
    full_url = f"{base_url}/{encoded_command}?access_token={settings.hubitat.access_token}"

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
    new_signal = sendFujitsuAC(new_bytes, len(new_bytes))

    # encode_ir automatically removes trailing gap (> 8000µs)
    new_command = encode_ir(new_signal)

    print(f"New: {new_command}")

    # Construct URL to send the new command to remote hub (from settings)
    base_url = f"https://cloud.hubitat.com/api/{settings.hubitat.hub_id}/apps/{settings.hubitat.api_app_id}/devices/{settings.hubitat.device_id}/sendCode"
    # URL-encode the command to handle special characters like / and +
    encoded_command = urllib.parse.quote(new_command, safe="")
    full_url = f"{base_url}/{encoded_command}?access_token={settings.hubitat.access_token}"

    print(f"\nSending to hub:")
    print(full_url)

    # Make API call to send the command
    response = requests.post(full_url, timeout=10)
    print(f"\nResponse status: {response.status_code}")
    print(f"Response body: {response.text}")
    response.raise_for_status()
    print("✓ Command sent successfully!")
