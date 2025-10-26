#!/bin/bash
# Vercel build script for C++ extensions
# This runs during Vercel's build phase to compile the IRremoteESP8266 bindings
# C++ bindings are REQUIRED - build will fail if they cannot be compiled

set -e  # Exit on error

echo "=================================================="
echo "Maestro Tuya IR Bridge - Vercel Build Script"
echo "=================================================="

# Install build dependencies
echo "Installing build dependencies..."
pip install --upgrade pip
pip install setuptools pybind11

# Build C++ extensions (REQUIRED)
echo ""
echo "Building C++ extensions (REQUIRED)..."
python setup.py build_ext --inplace

echo ""
echo "✅ C++ extensions built successfully!"
echo "   Enhanced protocol detection enabled"
echo "   - 20+ HVAC protocols"
echo "   - 40+ manufacturer variants"
echo ""
echo "Build complete!"
