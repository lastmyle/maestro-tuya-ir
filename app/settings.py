"""
Application Settings

Centralized configuration management using environment variables.
"""

import os
from typing import Optional
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class HubitatSettings(BaseSettings):
    """Hubitat integration settings for testing"""

    model_config = ConfigDict(
        env_prefix="HUBITAT_",
        case_sensitive=False,
    )

    hub_id: str = ""
    api_app_id: str = ""
    device_id: str = ""
    access_token: str = ""


class Settings(BaseSettings):
    """Application settings"""

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
    )

    # Server configuration
    port: int = 8002

    # Vercel configuration
    vercel_project_id: Optional[str] = None

    # Hubitat integration (optional, for testing)
    hubitat: HubitatSettings = HubitatSettings()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize hubitat settings from environment
        self.hubitat = HubitatSettings()


# Global settings instance
settings = Settings()
