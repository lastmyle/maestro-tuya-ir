"""
Maestro Tuya IR Bridge - FastAPI Application

Main entry point for the IR bridge service.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import decode, encode, generate, health, identify

# Create FastAPI app
app = FastAPI(
    title="Maestro Tuya IR Bridge",
    description=(
        "Translate, decode, and generate complete IR command sets "
        "for Tuya-based HVAC devices"
    ),
    version="1.0.0",
    docs_url="/",  # Swagger UI at root
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(decode.router, prefix="/api", tags=["decode"])
app.include_router(identify.router, prefix="/api", tags=["identify"])
app.include_router(generate.router, prefix="/api", tags=["generate"])
app.include_router(encode.router, prefix="/api", tags=["encode"])
app.include_router(health.router, prefix="/api", tags=["health"])


@app.get("/api")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Maestro Tuya IR Bridge",
        "version": "1.0.0",
        "description": "The conductor for your climate control codes",
        "endpoints": {
            "decode": "/api/decode",
            "identify": "/api/identify",
            "generate": "/api/generate",
            "encode": "/api/encode",
            "health": "/api/health",
        },
        "docs": "/",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
