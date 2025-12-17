import json
from datetime import datetime, timedelta
import os

USERS_FILE = r"d:\SITES\clipgenius\backend\storage\users.json"

def migrate_users():
    if not os.path.exists(USERS_FILE):
        print(f"File not found: {USERS_FILE}")
        return

    try:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
        
        updated_count = 0
        now = datetime.now()
        end_date = now + timedelta(days=30)
        
        for user in users:
            if user.get("plan") != "free":
                # Only update if dates are missing
                if "subscription_start_date" not in user:
                    user["subscription_start_date"] = now.isoformat()
                    user["subscription_end_date"] = end_date.isoformat()
                    updated_count += 1
                    print(f"Updated user {user.get('email')} - Plan: {user.get('plan')}")
        
        if updated_count > 0:
            with open(USERS_FILE, 'w') as f:
                json.dump(users, f, indent=2)
            print(f"Successfully migrated {updated_count} users.")
        else:
            print("No users needed migration.")
            
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate_users()
