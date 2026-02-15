"""
 FastAPI Application
Main application entry point with middleware, routes, and error handling
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os

from .core import settings, init_db, close_db, ping_db
from .core.database import get_db
from .core.s3_config import init_s3
from .core.admin_init import init_admin_user
from .api import content, contact, auth, upload, seo

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    # Startup
    logger.info("Starting up  API...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
        
        # Initialize admin user from .env if credentials exist
        db = await get_db()
        await init_admin_user(db)
        
        # Initialize S3 for image storage
        init_s3()
        logger.info("S3 storage initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down  API...")
    try:
        await close_db()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan
)


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)


# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    logger.debug(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.debug(f"Response status: {response.status_code}")
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unhandled exceptions"""
    logger.error(f"Unhandled exception in {request.url.path}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal Server Error",
            "detail": str(exc) if settings.DEBUG else "An error occurred processing your request"
        },
    )


# Include API routers
app.include_router(
    auth.router,
    prefix="/api/auth",  # ← Change this
    tags=["Authentication"]
)
app.include_router(
    content.router,
    prefix=settings.API_PREFIX,
    tags=["Content Management"]
)
app.include_router(
    contact.router,
    prefix=settings.API_PREFIX,
    tags=["Contact Management"]
)
app.include_router(
    upload.router,
    prefix=settings.API_PREFIX,
    tags=["File Upload"]
)
app.include_router(
    seo.router,
    tags=["SEO"]
)

# Serve uploaded files
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Root endpoint
@app.get("/")
async def read_root():
    """
    Root endpoint with API information
    
    Returns:
        API metadata and available endpoints
    """
    db_status = await ping_db()
    
    return {
        "message": "Welcome to  API",
        "version": settings.APP_VERSION,
        "status": "healthy" if db_status else "degraded",
        "database": "connected" if db_status else "disconnected",
        "documentation": "/docs",
        "openapi": "/openapi.json",
        "endpoints": {
            "content": f"{settings.API_PREFIX}/content",
            "contact": f"{settings.API_PREFIX}/contact",
            "health": "/health",
            "menus": "/menus"
        }
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        Application and database health status
    """
    db_status = await ping_db()
    
    return {
        "status": "healthy" if db_status else "degraded",
        "database": "connected" if db_status else "disconnected",
        "version": settings.APP_VERSION
    }


# Navigation menus endpoint
@app.get("/menus")
async def get_menus():
    """
    Get navigation menu structure for frontend
    
    Returns:
        Menu structure with categories and subcategories
    """
    return {
        "main_menus": [
            {
                "id": "home",
                "title": "Home",
                "path": "/",
                "description": "Home page"
            },
            {
                "id": "income-tax",
                "title": "Income Tax",
                "path": "/income-tax",
                "description": "Income Tax regulations and updates",
                "sub_menus": [
                    {"id": "articles", "title": "Articles", "path": "articles"},
                    {"id": "news", "title": "News", "path": "news"},
                    {"id": "judiciary", "title": "Judiciary", "path": "judiciary"}
                ]
            },
            {
                "id": "gst",
                "title": "GST",
                "path": "/gst",
                "description": "GST regulations and guidelines",
                "sub_menus": [
                    {"id": "articles", "title": "Articles", "path": "articles"},
                    {"id": "news", "title": "News", "path": "news"},
                    {"id": "judiciary", "title": "Judiciary", "path": "judiciary"}
                ]
            },
            {
                "id": "mca",
                "title": "MCA",
                "path": "/mca",
                "description": "Ministry of Corporate Affairs regulations",
                "sub_menus": [
                    {"id": "articles", "title": "Articles", "path": "articles"},
                    {"id": "news", "title": "News", "path": "news"},
                    {"id": "judiciary", "title": "Judiciary", "path": "judiciary"}
                ]
            },
            {
                "id": "sebi",
                "title": "SEBI",
                "path": "/sebi",
                "description": "Securities and Exchange Board of India",
                "sub_menus": [
                    {"id": "articles", "title": "Articles", "path": "articles"},
                    {"id": "news", "title": "News", "path": "news"},
                    {"id": "judiciary", "title": "Judiciary", "path": "judiciary"}
                ]
            },
            {
                "id": "ms-office",
                "title": "MS Office",
                "path": "/ms-office",
                "description": "MS Office guides and tutorials",
                "sub_menus": [
                    {"id": "articles", "title": "Articles", "path": "articles"},
                    {"id": "news", "title": "News", "path": "news"}
                ]
            },
            {
                "id": "about",
                "title": "About Us",
                "path": "/about-us",
                "description": "About our portal"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
