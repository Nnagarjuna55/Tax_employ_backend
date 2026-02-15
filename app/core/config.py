"""
Configuration settings for the  API
Centralized configuration management with environment variables
"""

import os
from typing import List, Optional
from dotenv import load_dotenv
import os.path

# Ensure we load the project's .env (backend/.env) explicitly
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DOTENV_PATH = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=DOTENV_PATH)


def _parse_db_from_mongo_url(url: Optional[str]) -> Optional[str]:
    """Parse the database name from a MongoDB URI if present.

    Examples:
    - mongodb://localhost:27017/tax -> 'tax'
    - mongodb://user:pass@host:27017/tax?authSource=admin -> 'tax'
    - mongodb://localhost:27017 -> None
    """
    if not url:
        return None
    try:
        # Strip params
        path = url.split('://', 1)[-1]
        if '/' not in path:
            return None
        remainder = path.split('/', 1)[1]
        db = remainder.split('?', 1)[0]
        return db if db else None
    except Exception:
        return None


class Settings:
    """Application settings"""
    
    # Application Info
    APP_NAME: str = " API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Smart tax solutions & compliance platform"
    
    # Database Configuration
    @staticmethod
    def _get_mongo_url() -> str:
        """Get MongoDB URL with SSL parameters for Atlas connections"""
        url = os.getenv("MONGO_URL", "mongodb+srv://mahendarfcl_db_user:BLiNOgqwIY9IpjKD@cluster0.0t1cob5.mongodb.net/TaxEmployee")
        # Add SSL parameters for MongoDB Atlas connections if not already present
        if "mongodb.net" in url and "?" not in url:
            # Atlas connections need specific parameters to handle certificate verification
            url = f"{url}?retryWrites=false&w=majority&serverSelectionTimeoutMS=5000&socketTimeoutMS=45000&maxIdleTimeMS=45000"
        return url
    
    MONGO_URL: str = _get_mongo_url()
    # Prefer explicit DATABASE_NAME env var; otherwise derive from MONGO_URL if present
    _derived_db = _parse_db_from_mongo_url(os.getenv("MONGO_URL"))
    DATABASE_NAME: str = os.getenv("DATABASE_NAME") or _derived_db or "tax_portal"
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    RELOAD: bool = os.getenv("RELOAD", "True").lower() == "true"
    
    # CORS Configuration
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://taxemployee.com",
        "https://www.taxemployee.com",
    ]
    CORS_ORIGINS: List[str] = ALLOWED_HOSTS + [FRONTEND_URL]
    
    # Workers Configuration
    WORKERS: int = int(os.getenv("WORKERS", 1))
    
    # API Configuration
    API_PREFIX: str = "/api"
    API_VERSION_PREFIX: str = "/v1"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Pagination defaults
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100
    
    # Content defaults
    MIN_CONTENT_LENGTH: int = 10
    MAX_SUMMARY_LENGTH: int = 500
    MIN_TITLE_LENGTH: int = 1
    MAX_TITLE_LENGTH: int = 500


# Create settings instance
settings = Settings()
