#!/usr/bin/env python3
"""
Generate a markdown file with Fujitsu IR test codes.
"""

from fastapi.testclient import TestClient

from index import app

client = TestClient(app)

# Real Fujitsu code
code = (
    "Ed4MRQYFAkQBxAGIAcQBwATEAYAHQBMAiKABA8QBwASAA0ALQAMGRAHEAcAEiCADA8QBiAGA"
    "A0ATgAvAAUAPQAFAB4ADAsQBiGABQDfAL8AHAIhgAQDEIAEBiAHgAR8BiAFAD0ABQBMBwARA"
    "B0ADQAtAA0ALQAMBxAHARwjABIgBiAHEAYhgAUAH4AcDAYgBQCNAAwGIAYAbQAsCxAGIoAEB"
    "xAFAS0ADQAsDwATEAcALQA8AiKABwAlABwHEAYAhQAECxAGIYAFAB+ADA4ABQBGAAQDEIAEB"
    "RAFBZ0AHAsQBiCABgAUBiAGAB0AFAcQBgBsCxAGIYAHAB0ABAcQB4BMbQLcAiKABAcAE4AU"
    "DQAELwATEAYgBxAGIAYgB"
)

# Identify
identify_resp = client.post("/api/identify", json={"tuyaCode": code})
identify_data = identify_resp.json()

output = []
output.append("# Fujitsu HVAC IR Commands for Testing\n")
output.append(f'**Manufacturer:** {identify_data["manufacturer"]}\n')
output.append(f'**Protocol:** {identify_data["protocol"]}\n')
output.append("\n")

# Generate all modes at 24C
gen_resp = client.post(
    "/api/generate",
    json={
        "manufacturer": identify_data["manufacturer"],
        "protocol": identify_data["protocol"],
        "filter": {
            "modes": ["cool", "heat", "dry", "fan", "auto"],
            "tempRange": [24, 24],
            "fanSpeeds": ["auto", "low", "medium", "high", "quiet"],
        },
    },
)

data = gen_resp.json()
commands = data["commands"]

output.append("## Test Commands - 24°C All Modes & Fan Speeds\n\n")
output.append("Copy these Tuya IR codes to your IR blaster device for testing:\n\n")

# Off command
output.append("### Power Off\n")
output.append("```\n")
output.append(f'{commands["off"]}\n')
output.append("```\n\n")

# Each mode
for mode in ["cool", "heat", "dry", "fan", "auto"]:
    if mode in commands:
        output.append(f"### {mode.title()} Mode - 24°C\n\n")
        for fan, temps in commands[mode].items():
            if "24" in temps:
                output.append(f"**Fan: {fan.title()}**\n")
                output.append("```\n")
                output.append(f'{temps["24"]}\n')
                output.append("```\n\n")

# Temperature range for cool mode
output.append("## Temperature Range - Cool Mode, Auto Fan\n\n")
gen_resp2 = client.post(
    "/api/generate",
    json={
        "manufacturer": identify_data["manufacturer"],
        "protocol": identify_data["protocol"],
        "filter": {
            "modes": ["cool"],
            "tempRange": [20, 28],
            "fanSpeeds": ["auto"],
        },
    },
)
data2 = gen_resp2.json()

for temp in range(20, 29):
    if str(temp) in data2["commands"]["cool"]["auto"]:
        output.append(f"**{temp}°C**\n")
        output.append("```\n")
        output.append(f'{data2["commands"]["cool"]["auto"][str(temp)]}\n')
        output.append("```\n\n")

# Write to file
with open("FUJITSU_TEST_CODES.md", "w") as f:
    f.write("".join(output))

print("✅ Generated FUJITSU_TEST_CODES.md")
print(f"   Total modes: {len([m for m in commands.keys() if m != 'off'])}")
total_codes = sum(
    1 for m in commands.values() if isinstance(m, dict) for f in m.values() for t in f.values()
) + 1
print(f"   Total test codes: {total_codes}")
