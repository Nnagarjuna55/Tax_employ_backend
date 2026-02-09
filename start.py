#!/usr/bin/env python
"""
 API Development Server Startup Script
Runs the FastAPI application with uvicorn in development mode
"""

import os
import sys
import uvicorn
import logging
from dotenv import load_dotenv

# Ensure the current directory is in the path
sys.path.insert(0, os.getcwd())

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Get configuration from environment
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
RELOAD = os.getenv("RELOAD", "True").lower() == "true"

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 Starting  API (Development Mode)")
    logger.info("=" * 60)
    logger.info(f"📍 Server: http://{HOST}:{PORT}")
    logger.info(f"📚 API Docs: http://{HOST}:{PORT}/docs")
    logger.info(f"🔍 ReDoc: http://{HOST}:{PORT}/redoc")
    logger.info(f"❤️  Health Check: http://{HOST}:{PORT}/health")
    logger.info(f"📋 Menus: http://{HOST}:{PORT}/menus")
    logger.info(f"🔧 Debug Mode: {DEBUG}")
    logger.info(f"♻️  Auto-reload: {RELOAD}")
    logger.info("=" * 60)
    
    try:
        uvicorn.run(
            "app.main:app",
            host=HOST,
            port=PORT,
            reload=RELOAD,
            reload_dirs=["app"] if RELOAD else None,
            log_level="info" if not DEBUG else "debug",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Error starting server: {str(e)}")
        sys.exit(1)
