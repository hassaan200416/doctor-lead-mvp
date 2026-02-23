"""Application configuration settings."""
from pathlib import Path
from pydantic_settings import BaseSettings


# Get the path to the backend directory (3 levels up from this file)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Application settings management."""
    
    # Database - REQUIRED from .env file
    DATABASE_URL: str
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Doctor Lead MVP"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = str(ENV_FILE)
        case_sensitive = True


settings = Settings()
