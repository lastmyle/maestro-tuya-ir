#!/usr/bin/env python3
"""
Build script for C++ extensions.

This script is called automatically during installation to build the
IRremoteESP8266 Python bindings. C++ bindings are REQUIRED.
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Build C++ extensions (REQUIRED)."""
    project_root = Path(__file__).parent.parent

    print("=" * 60)
    print("Building IRremoteESP8266 C++ Bindings (REQUIRED)")
    print("=" * 60)

    try:
        # Run setup.py build_ext --inplace
        result = subprocess.run(
            [sys.executable, "setup.py", "build_ext", "--inplace"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ C++ extensions built successfully!")
            print("\nExtended protocol detection enabled:")
            print("  - 20+ HVAC protocols")
            print("  - 40+ manufacturer variants")
            print("  - Enhanced accuracy with IRremoteESP8266")
            return 0
        else:
            print("❌ C++ extension build FAILED")
            print("\nC++ bindings are REQUIRED for this application.")
            print("\nBuild output:")
            print(result.stderr)
            print("\nTo fix this, ensure you have:")
            print("  - A C++ compiler (gcc, clang, or MSVC)")
            print("  - pybind11 installed (uv sync --all-extras)")
            return 1  # Return error code to fail installation

    except Exception as e:
        print(f"❌ Error building C++ extensions: {e}")
        print("\nC++ bindings are REQUIRED for this application.")
        return 1  # Return error code to fail installation


if __name__ == "__main__":
    sys.exit(main())
