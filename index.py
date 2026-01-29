"""
Maestro Tuya IR Bridge - Main FastAPI Application

This is the main entry point for the Maestro Tuya IR Bridge service.
It provides endpoints for:
  1. GET /api/manufacturers - List manufacturers with known good codes
  2. POST /api/generate-from-manufacturer - Generate commands from known codes
  3. POST /api/identify - Identify protocol from Tuya IR code and generate commands
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.api.identify import router as identify_router
from app.api.manufacturers import router as manufacturers_router

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

# Register routers
app.include_router(identify_router, prefix="/api", tags=["identify"])
app.include_router(manufacturers_router, prefix="/api", tags=["manufacturers"])


# Redirect root to Swagger UI
@app.get("/", include_in_schema=False)
async def root():
    """Redirect to Swagger UI documentation"""
    return RedirectResponse(url="/docs")
