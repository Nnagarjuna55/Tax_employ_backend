"""
Initialize Admin User from Environment Variables
Automatically creates admin user on server startup if credentials are in .env
"""
import os
import hashlib
import logging
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Hash password using SHA256 (same as auth.py)"""
    return hashlib.sha256(password.encode()).hexdigest()


async def init_admin_user(db: AsyncIOMotorDatabase) -> bool:
    """
    Initialize admin user from environment variables
    Returns True if admin was created/updated, False otherwise
    """
    try:
        # Get credentials from environment
        admin_email = os.environ.get('ADMIN_EMAIL')
        admin_password = os.environ.get('ADMIN_PASSWORD')
        admin_name = os.environ.get('ADMIN_NAME', ' Administrator')
        
        if not admin_email or not admin_password:
            logger.warning("ADMIN_EMAIL or ADMIN_PASSWORD not found in environment variables")
            logger.info("Admin user will not be auto-created. Use init_admin.py script to create admin manually.")
            return False
        
        users_collection = db.get_collection('users')
        
        # Check if admin already exists
        existing = await users_collection.find_one({'email': admin_email})
        
        if existing:
            # Update existing user to ensure it's admin
            await users_collection.update_one(
                {'_id': existing['_id']},
                {'$set': {
                    'is_admin': True,
                    'password': hash_password(admin_password),
                    'name': admin_name,
                    'updated_at': datetime.utcnow(),
                    'roles': ['admin']
                }}
            )
            logger.info(f"✅ Updated admin user: {admin_email}")
        else:
            # Create new admin user
            user = {
                'email': admin_email,
                'name': admin_name,
                'password': hash_password(admin_password),
                'is_admin': True,
                'created_at': datetime.utcnow(),
                'roles': ['admin']
            }
            result = await users_collection.insert_one(user)
            logger.info(f"✅ Created admin user: {admin_email} (ID: {result.inserted_id})")
        
        logger.info(f"📋 Admin credentials: {admin_email} / {admin_password}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error initializing admin user: {str(e)}")
        return False
