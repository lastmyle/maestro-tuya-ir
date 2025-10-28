"""
Maestro Tuya IR Bridge - Main FastAPI Application

This is the main entry point for the Maestro Tuya IR Bridge service.
It provides a unified API endpoint for IR code analysis and command generation.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.analyze import router as analyze_router
from app.api.health import router as health_router

# Create FastAPI app
app = FastAPI(
    title="Maestro Tuya IR Bridge",
    description="Translates, decodes, and generates complete IR command sets for Tuya-based HVAC devices",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now - tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(analyze_router, prefix="/api", tags=["analyze"])
app.include_router(health_router, prefix="/api", tags=["health"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - returns service information"""
    return {
        "service": "Maestro Tuya IR Bridge",
        "version": "1.0.0",
        "description": "Unified IR code analysis and command generation for HVAC devices",
        "docs": "/docs",
        "endpoints": {
            "analyze": "/api/identify",
            "health": "/api/health"
        },
        "supported_protocols": {
            "manufacturers": [
                "Fujitsu",
                "Gree",
                "Daikin (10 variants)",
                "Mitsubishi (5 variants)",
                "Hitachi (8 variants)",
                "Panasonic (3 variants)",
                "Samsung (3 variants)",
                "LG (2 variants)",
                "Carrier (5 variants)"
            ],
            "total_variants": 36
        }
    }
