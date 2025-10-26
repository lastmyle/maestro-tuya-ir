"""
Setup script for building C++ bindings using pybind11.
"""


from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

# Read version from pyproject.toml
__version__ = "1.0.0"

# Define the extension module
ext_modules = [
    Pybind11Extension(
        "_irremote",
        sources=["bindings/irremote/irremote_bindings.cpp"],
        include_dirs=[
            "bindings/irremote",
        ],
        cxx_std=11,  # C++11 standard required for pybind11
        define_macros=[("VERSION_INFO", __version__)],
    ),
]

setup(
    name="maestro-tuya-ir-bridge",
    version=__version__,
    description="Python bindings for IRremoteESP8266 protocol database",
    long_description="",
    packages=["app"],  # Only include app package
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.12",
)
