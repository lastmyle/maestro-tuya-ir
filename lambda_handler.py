"""
AWS Lambda handler for Maestro Tuya IR Bridge.

This module provides the Mangum ASGI adapter to run FastAPI on AWS Lambda.
"""

from mangum import Mangum
from index import app

# Create Lambda handler with Mangum
# lifespan="off" disables lifespan events for Lambda (not needed in serverless)
handler = Mangum(app, lifespan="off")
