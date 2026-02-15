"""
Database initialization and connection management
Handles MongoDB async connections and indexing
"""

import motor.motor_asyncio
import logging
from typing import Optional
from .config import settings

logger = logging.getLogger(__name__)

# Global database client and instance
_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
_database: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None


async def init_db() -> None:
    """Initialize database connection"""
    global _client, _database
    
    try:
        logger.info(f"Attempting to connect to MongoDB: {settings.MONGO_URL[:50]}...")
        
        # Create MongoDB connection with SSL/TLS settings
        # mongodb+srv:// automatically enables TLS, tlsInsecure=True disables hostname verification
        _client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.MONGO_URL,
            tlsInsecure=True,  # Accept self-signed certificates and skip hostname verification
            tlsCAFile=None,  # Don't use custom CA bundle
            serverSelectionTimeoutMS=15000,
            connectTimeoutMS=15000,
            socketTimeoutMS=60000,
            maxIdleTimeMS=45000,
            retryWrites=True,
            maxPoolSize=50,
            minPoolSize=10,
        )
        _database = _client[settings.DATABASE_NAME]
        
        # Verify connection - use async/await properly
        logger.info("Verifying MongoDB connection...")
        await _database.command('ping')
        logger.info(f"Database connection successful: {settings.DATABASE_NAME}")
        
        # Initialize indexes
        await init_indexes()
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        logger.error(f"MongoDB URL: {settings.MONGO_URL[:100]}")
        raise


async def close_db() -> None:
    """Close database connection"""
    global _client
    
    try:
        if _client:
            _client.close()
            logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database: {str(e)}")


async def get_db() -> motor.motor_asyncio.AsyncIOMotorDatabase:
    """Get database instance"""
    if _database is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _database


async def ping_db() -> bool:
    """
    Ping the database to check connection status
    
    Returns:
        bool: True if connected, False otherwise
    """
    try:
        if _database:
            await _database.command('ping')
            return True
        return False
    except Exception as e:
        logger.error(f"Database ping failed: {str(e)}")
        return False


async def init_indexes() -> None:
    """
    Initialize database indexes for better query performance
    Creates compound indexes and text indexes
    """
    if _database is None:
        logger.warning("Database not initialized for indexing")
        return
    
    try:
        # Get collections
        content_collection = _database.get_collection("contents")
        contact_collection = _database.get_collection("contacts")
        
        # Content collection indexes
        await content_collection.create_index([("category", 1)])
        await content_collection.create_index([("type", 1)])
        await content_collection.create_index([("date", -1)])
        await content_collection.create_index([
            ("title", "text"),
            ("body", "text"),
            ("summary", "text")
        ])
        
        # Contact collection indexes
        await contact_collection.create_index([("email", 1)])
        await contact_collection.create_index([("date", -1)])
        await contact_collection.create_index([("status", 1)])
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {str(e)}")


# Dependency for getting database collections
async def get_content_collection():
    """Get content collection"""
    db = await get_db()
    return db.get_collection("contents")


async def get_contact_collection():
    """Get contact collection"""
    db = await get_db()
    return db.get_collection("contacts")
