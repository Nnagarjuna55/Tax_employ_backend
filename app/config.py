"""Configuration settings for the  API"""

import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://mahendarfcl_db_user:BLiNOgqwIY9IpjKD@cluster0.0t1cob5.mongodb.net")
DATABASE_NAME = os.getenv("DATABASE_NAME", "taxemploy")

# API Configuration
API_TITLE = " API"
API_VERSION = "1.0.0"

# CORS Configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    FRONTEND_URL
]

# Server Configuration
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
