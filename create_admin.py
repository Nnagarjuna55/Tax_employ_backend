#!/usr/bin/env python3
"""
create_admin.py

Usage:
  python create_admin.py --email admin@example.com --password yourpassword

This script will create an admin user in the MongoDB configured by the `MONGO_URL` env var
or in `backend/.env` if present. It hashes the password with SHA256 (same as the app's auth logic).
"""
import argparse
import os
import hashlib
from datetime import datetime
import traceback

from pymongo import MongoClient
from bson import ObjectId

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
except Exception:
    pass


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def get_mongo_client():
    mongo_url = os.environ.get('MONGO_URL') or 'mongodb://localhost:27017'
    return MongoClient(mongo_url)


def create_admin(email: str, password: str, name: str = 'Administrator'):
    client = get_mongo_client()
    # Determine which database to use:
    # 1. Use DATABASE_NAME env var if present
    # 2. Otherwise, use the database specified in the Mongo URI (get_default_database)
    # 3. Fallback to 'tax_portal'
    db_name = os.environ.get('DATABASE_NAME')
    if db_name:
        db = client[db_name]
    else:
        try:
            db = client.get_default_database()
            # get_default_database may return a Database even when none specified; ensure it has a name
            if not getattr(db, 'name', None):
                raise Exception("No default database in URI")
        except Exception:
            db = client['tax_portal']
    users = db.get_collection('users')

    # Diagnostic: verify connection
    try:
        client.admin.command('ping')
        print(f"Connected to MongoDB server; using database: '{db.name}'")
    except Exception as e:
        print("Warning: Unable to ping MongoDB server. Connection/auth may fail.")
        print(str(e))

    existing = users.find_one({'email': email})
    if existing:
        print(f"User with email {email} already exists (id={existing.get('_id')}). Updating to admin and setting password.")
        users.update_one({'_id': existing['_id']}, {'$set': {
            'is_admin': True,
            'password': hash_password(password),
            'name': name,
            'updated_at': datetime.utcnow()
        }})
        return existing['_id']

    user = {
        'email': email,
        'name': name,
        'password': hash_password(password),
        'is_admin': True,
        'created_at': datetime.utcnow(),
        'roles': ['admin']
    }

    result = users.insert_one(user)
    print(f"Created admin user: {email} with id: {result.inserted_id} in database '{db.name}'")
    return result.inserted_id


def main():
    parser = argparse.ArgumentParser(description='Create or update an admin user in MongoDB')
    parser.add_argument('--email', required=True, help='Admin email')
    parser.add_argument('--password', required=True, help='Admin password')
    parser.add_argument('--name', default='Administrator', help='Admin display name')

    args = parser.parse_args()

    try:
        uid = create_admin(args.email, args.password, args.name)
        print('Done. Use these credentials to log in:')
        print(f'  email: {args.email}')
        print(f'  password: {args.password}')
    except Exception as e:
        print('Error creating admin user:')
        print(str(e))
        traceback.print_exc()


if __name__ == '__main__':
    main()
