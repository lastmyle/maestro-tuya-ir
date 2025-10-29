"""
Maestro Tuya IR Bridge - Main FastAPI Application

This is the main entry point for the Maestro Tuya IR Bridge service.
It provides two endpoints:
  1. GET /api/manufacturers - List all supported manufacturers
  2. POST /api/identify - Identify protocol from Tuya IR code and generate commands
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.api.analyze import router as analyze_router

# Create FastAPI app with Swagger UI at root
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

# Register router with both endpoints
app.include_router(analyze_router, prefix="/api", tags=["analyze"])


# Redirect root to Swagger UI
@app.get("/", include_in_schema=False)
async def root():
    """Redirect to Swagger UI documentation"""
    return RedirectResponse(url="/docs")
