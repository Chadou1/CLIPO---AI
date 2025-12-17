import sys
import os
from datetime import datetime

# Add current directory to path so we can import utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.file_storage import get_storage
# from utils.auth import get_password_hash # passlib is failing
import bcrypt

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def reset_users():
    storage = get_storage()
    
    # Clear existing users
    print("Clearing all users...")
    storage._write_json(storage.files["users"], [])
    
    # Create admin user
    print("Creating admin user...")
    admin_email = "admin@clipo.ai"
    admin_password = "admin" 
    
    user_data = {
        "email": admin_email,
        "password_hash": get_password_hash(admin_password),
        "credits": 999999, # Unlimited
        "plan": "agency",
        "email_verified": True,
        "created_at": datetime.utcnow().isoformat()
    }
    
    created_user = storage.create_user(user_data)
    
    print(f"Admin user created successfully:")
    print(f"Email: {admin_email}")
    print(f"Password: {admin_password}")
    print(f"Plan: {created_user['plan']}")
    print(f"Credits: {created_user['credits']}")

if __name__ == "__main__":
    reset_users()
