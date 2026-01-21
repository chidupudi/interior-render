"""
Configuration settings for the Interior Design System.
Loads from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Paths
    BASE_DIR: str = str(Path(__file__).parent.parent.parent.absolute())
    BLENDER_PATH: str = os.getenv("BLENDER_PATH", "/usr/bin/blender")
    BLENDER_SCRIPTS_DIR: str = os.getenv(
        "BLENDER_SCRIPTS_DIR",
        str(Path(__file__).parent.parent.parent.parent / "blender" / "scripts")
    )
    OUTPUT_DIR: str = os.getenv(
        "OUTPUT_DIR",
        str(Path(__file__).parent.parent.parent / "output")
    )
    SCENES_DIR: str = os.getenv(
        "SCENES_DIR",
        str(Path(__file__).parent.parent.parent / "scenes")
    )
    UPLOADS_DIR: str = os.getenv(
        "UPLOADS_DIR",
        str(Path(__file__).parent.parent.parent / "uploads")
    )
    ASSETS_DIR: str = os.getenv(
        "ASSETS_DIR",
        str(Path(__file__).parent.parent.parent.parent / "blender" / "assets")
    )

    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Blender settings
    BLENDER_TIMEOUT: int = int(os.getenv("BLENDER_TIMEOUT", "120"))  # seconds
    USE_MOCK_BLENDER: bool = os.getenv("USE_MOCK_BLENDER", "false").lower() == "true"
    USE_MOCK_GEMINI: bool = os.getenv("USE_MOCK_GEMINI", "false").lower() == "true"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton settings instance
settings = Settings()
