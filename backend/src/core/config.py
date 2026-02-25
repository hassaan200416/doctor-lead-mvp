"""
FILE PURPOSE:
This file loads and manages all the configuration settings for the backend.
Configuration values come from the .env file (which is not shared in version control for security).

Configuration includes:
- Database connection URL
- API version prefix
- Security settings like API keys and token expiration
- CORS origins (which websites can access this backend)
- External service API keys (like email validation)

THINK OF IT AS: The "settings file" that contains all important values the backend needs.
"""

# Import tools for loading settings
from pathlib import Path  # Tool for file path handling
from pydantic_settings import BaseSettings  # Tool to load and validate settings from .env file


# Find the path to the .env file
# This goes up 3 folder levels from where this file is located:
# src/core/config.py -> src/core -> src -> backend -> .env
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Build the full path to the .env file (where secrets are stored)
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """
    Settings class that loads configuration from .env file.
    
    HOW IT WORKS:
    - This class defines what settings we need
    - Pydantic automatically loads matching values from the .env file
    - If a required setting is missing, the app will fail to start
    """
    
    # DATABASE CONNECTION (required - app won't start without this)
    # Format: postgresql://username:password@host:port/database_name
    DATABASE_URL: str = ""
    
    # API PATHS
    # This prefix is added to all API routes (e.g., /api/v1/leads)
    API_V1_PREFIX: str = "/api/v1"
    
    # Name of the project (used in documentation)
    PROJECT_NAME: str = "Doctor Lead MVP"
    
    # CORS CONFIGURATION (allows these websites to access the backend)
    # Add your frontend URL here so it can make requests
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",  # Vite dev server on Windows
        "http://localhost:3000",  # Alternative frontend port
    ]
    
    # SECURITY SETTINGS
    # How long an access token stays valid (in minutes)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Secret API key required to use the /leads endpoints
    # Anyone making requests must include this in the X-API-Key header
    API_KEY: str | None = None

    # EXTERNAL SERVICE KEYS
    # API key for Abstract's email validation service (optional)
    # Get this from https://www.abstractapi.com/api/email-validation
    ABSTRACT_EMAIL_API_KEY: str | None = None
    
    class Config:
        # Pydantic configuration: tells it to load from .env file
        env_file = str(ENV_FILE)  # Load variables from the .env file
        case_sensitive = True  # Require exact case matching (DATABASE_URL not database_url)


# Create the settings object that other files import
# This reads the .env file when the backend starts
settings = Settings()
