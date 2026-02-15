#!/usr/bin/env python3
"""
Test MongoDB Atlas connection
Run this to diagnose connection issues
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://mahendarfcl_db_user:BLiNOgqwIY9IpjKD@cluster0.0t1cob5.mongodb.net/taxemployee")

print("=" * 60)
print("🧪 Testing MongoDB Atlas Connection")
print("=" * 60)
print(f"\n📍 Connection String:")
print(f"   {MONGO_URL[:80]}...")

try:
    print("\n⏳ Attempting connection (this may take a moment)...\n")
    
    from pymongo import MongoClient
    from pymongo.errors import ServerSelectionTimeoutError, OperationFailure
    
    # Try to connect with same settings as the app
    client = MongoClient(
        MONGO_URL,
        tlsInsecure=True,
        serverSelectionTimeoutMS=15000,
        connectTimeoutMS=15000,
        socketTimeoutMS=60000,
    )
    
    # Try to ping
    client.admin.command('ping')
    
    print("✅ SUCCESS! MongoDB connection works!\n")
    
    # List databases
    databases = client.list_database_names()
    print(f"📦 Available databases ({len(databases)}):")
    for db in databases[:10]:  # Show first 10
        print(f"   - {db}")
    
    # Check taxemployee database
    if "taxemployee" in databases:
        print(f"\n✅ Database 'taxemployee' exists!")
        db = client["taxemployee"]
        collections = db.list_collection_names()
        print(f"   Collections: {', '.join(collections) if collections else 'None (empty database)'}")
    else:
        print(f"\n⚠️  Database 'taxemployee' not found")
        print(f"   Available: {', '.join(databases)}")
    
    client.close()
    sys.exit(0)
    
except ServerSelectionTimeoutError as e:
    print("❌ TIMEOUT: Cannot reach MongoDB server\n")
    print("Likely causes:")
    print("  1. MongoDB Atlas IP whitelist not configured")
    print("     → Go to: https://cloud.mongodb.com → Network Access")
    print("     → Add your current IP address")
    print("  2. Network/firewall blocking port 27017")
    print("  3. MongoDB Atlas cluster is paused")
    print("\n" + "=" * 60)
    print("Full error:")
    print(str(e)[:500])
    sys.exit(1)
    
except OperationFailure as e:
    print("❌ AUTHENTICATION FAILED\n")
    print("Issue: Cannot authenticate with MongoDB")
    print("Check:")
    print("  1. Username is correct: mahendarfcl_db_user")
    print("  2. Password is correct: BLiNOgqwIY9IpjKD")
    print("  3. Database name is correct: taxemployee")
    print("\n" + "=" * 60)
    print("Full error:")
    print(str(e))
    sys.exit(1)
    
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}\n")
    print(str(e)[:500])
    sys.exit(1)
