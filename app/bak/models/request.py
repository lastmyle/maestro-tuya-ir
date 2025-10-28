"""
Request models for API endpoints.
"""

from typing import Optional

from pydantic import BaseModel, Field


class DecodeRequest(BaseModel):
    """Request model for /api/decode endpoint."""

    tuyaCode: str = Field(..., description="Base64 encoded Tuya IR code")


class IdentifyRequest(BaseModel):
    """Request model for /api/identify endpoint."""

    tuyaCode: str = Field(..., description="Base64 encoded Tuya IR code")
    manufacturer: Optional[str] = Field(None, description="Optional manufacturer hint")


class GenerateRequest(BaseModel):
    """Request model for /api/generate endpoint."""

    manufacturer: str = Field(..., description="Manufacturer name (e.g., 'Fujitsu')")
    protocol: str = Field(..., description="Protocol name (e.g., 'fujitsu_ac')")
    filter: Optional["GenerateFilter"] = Field(None, description="Optional filter criteria")
    sampleCode: Optional[str] = Field(
        None,
        description="Optional sample Tuya IR code for variant detection (Fujitsu only)",
    )


class GenerateFilter(BaseModel):
    """Filter criteria for command generation."""

    modes: Optional[list[str]] = Field(None, description="Modes to generate")
    tempRange: Optional[list[int]] = Field(
        None, description="Temperature range [min, max]", min_length=2, max_length=2
    )
    fanSpeeds: Optional[list[str]] = Field(None, description="Fan speeds to generate")


class EncodeRequest(BaseModel):
    """Request model for /api/encode endpoint."""

    manufacturer: str = Field(..., description="Manufacturer name")
    protocol: str = Field(..., description="Protocol name")
    command: "CommandParameters" = Field(..., description="HVAC command parameters")


class CommandParameters(BaseModel):
    """HVAC command parameters."""

    power: str = Field("on", description="Power state: 'on' or 'off'")
    mode: str = Field("cool", description="HVAC mode: cool, heat, dry, fan, auto")
    temperature: int = Field(24, description="Temperature in Celsius", ge=16, le=30)
    fan: str = Field("auto", description="Fan speed: auto, low, medium, high")
    swing: str = Field("off", description="Swing state: 'on' or 'off'")
