#!/usr/bin/env python3
"""
Initialize Admin User from .env file
This script automatically creates an admin user using credentials from .env file
Run this script once to set up the admin user, or it will run automatically on server start
"""
import os
import sys
import hashlib
from datetime import datetime

from pymongo import MongoClient
from bson import ObjectId

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
except Exception:
    pass


def hash_password(password: str) -> str:
    """Hash password using SHA256 (same as auth.py)"""
    return hashlib.sha256(password.encode()).hexdigest()


def get_mongo_client():
    """Get MongoDB client from environment"""
    mongo_url = os.environ.get('MONGO_URL') or 'mongodb://localhost:27017'
    return MongoClient(mongo_url)


def init_admin_from_env():
    """Create or update admin user from .env file credentials"""
    # Get credentials from environment
    admin_email = os.environ.get('ADMIN_EMAIL')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    admin_name = os.environ.get('ADMIN_NAME', 'Administrator')
    
    if not admin_email or not admin_password:
        print("⚠️  Warning: ADMIN_EMAIL or ADMIN_PASSWORD not found in .env file")
        print("   Please add the following to your .env file:")
        print("   ADMIN_EMAIL=admin@.com")
        print("   ADMIN_PASSWORD=your_secure_password")
        print("   ADMIN_NAME= Administrator")
        return False
    
    try:
        client = get_mongo_client()
        
        # Determine database
        db_name = os.environ.get('DATABASE_NAME')
        if db_name:
            db = client[db_name]
        else:
            try:
                db = client.get_default_database()
                if not getattr(db, 'name', None):
                    raise Exception("No default database in URI")
            except Exception:
                db = client['tax_portal']
        
        users = db.get_collection('users')
        
        # Check if admin already exists
        existing = users.find_one({'email': admin_email})
        
        if existing:
            # Update existing user to ensure it's admin
            users.update_one(
                {'_id': existing['_id']},
                {'$set': {
                    'is_admin': True,
                    'password': hash_password(admin_password),
                    'name': admin_name,
                    'updated_at': datetime.utcnow(),
                    'roles': ['admin']
                }}
            )
            print(f"✅ Updated admin user: {admin_email}")
            print(f"   Database: {db.name}")
            print(f"   User ID: {existing['_id']}")
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
            result = users.insert_one(user)
            print(f"✅ Created admin user: {admin_email}")
            print(f"   Database: {db.name}")
            print(f"   User ID: {result.inserted_id}")
        
        print("\n📋 Admin Login Credentials:")
        print(f"   Email: {admin_email}")
        print(f"   Password: {admin_password}")
        print(f"   Name: {admin_name}")
        print("\n⚠️  Keep these credentials secure!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing admin user: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("🚀 Initializing Admin User from .env file...\n")
    success = init_admin_from_env()
    sys.exit(0 if success else 1)
