"""
Response models for API endpoints.
"""

from typing import Any, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response."""

    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[str] = Field(None, description="Additional error details")


class DecodeResponse(BaseModel):
    """Response model for /api/decode endpoint."""

    success: bool = Field(True, description="Operation success status")
    timings: list[int] = Field(..., description="Raw IR timing array in microseconds")
    protocol: Optional["ProtocolInfo"] = Field(None, description="Detected protocol information")
    state: Optional[dict[str, Any]] = Field(None, description="Decoded HVAC state")


class ProtocolInfo(BaseModel):
    """Protocol identification information."""

    name: str = Field(..., description="Protocol name")
    manufacturer: str = Field(..., description="Manufacturer name")
    confidence: float = Field(..., description="Detection confidence (0-1)")


class IdentifyResponse(BaseModel):
    """Response model for /api/identify endpoint."""

    success: bool = Field(True, description="Operation success status")
    manufacturer: str = Field(..., description="Detected manufacturer")
    protocol: str = Field(..., description="Detected protocol name")
    modelFamily: Optional[str] = Field(None, description="Model family if detected")
    capabilities: dict[str, Any] = Field(..., description="Device capabilities")
    detectedState: Optional[dict[str, Any]] = Field(
        None, description="Current state detected from code"
    )


class GenerateResponse(BaseModel):
    """Response model for /api/generate endpoint."""

    success: bool = Field(True, description="Operation success status")
    manufacturer: str = Field(..., description="Manufacturer name")
    protocol: str = Field(..., description="Protocol name")
    totalCommands: int = Field(..., description="Total number of commands generated")
    commands: dict[str, Any] = Field(..., description="Generated command set")


class EncodeResponse(BaseModel):
    """Response model for /api/encode endpoint."""

    success: bool = Field(True, description="Operation success status")
    tuyaCode: str = Field(..., description="Base64 encoded Tuya IR code")
    timings: list[int] = Field(..., description="Raw IR timing array")
    timingsLength: int = Field(..., description="Number of timing values")


class HealthResponse(BaseModel):
    """Response model for /api/health endpoint."""

    status: str = Field("ok", description="Service status")
    supportedManufacturers: list[str] = Field(..., description="List of supported manufacturers")
    version: str = Field("1.0.0", description="API version")
