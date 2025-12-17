from utils.file_storage import get_storage
from utils.auth import get_password_hash
from datetime import datetime

def create_premium_account():
    """Create a premium account with unlimited access"""
    storage = get_storage()
    
    # Check if admin account already exists
    existing_user = storage.get_user_by_email("admin@clipgenius.ai")
    if existing_user:
        print("✅ Compte premium admin@clipgenius.ai existe déjà")
        return existing_user
    
    # Create premium account
    user_data = {
        "email": "admin@clipgenius.ai",
        "password_hash": get_password_hash("admin123"),
        "credits": 999999,  # Unlimited credits
        "plan": "agency",  # Best plan
        "created_at": datetime.utcnow().isoformat()
    }
    
    user = storage.create_user(user_data)
    print(f"✅ Compte premium créé avec succès")
    print(f"   📧 Email: admin@clipgenius.ai")
    print(f"   🔑 Mot de passe: admin123")
    print(f"   💎 Plan: AGENCY (illimité)")
    print(f"   ⭐ Crédits: 999999")
    
    return user

if __name__ == "__main__":
    create_premium_account()
