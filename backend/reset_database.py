"""
Script to reset the database - removes all users, clips, and creates a new admin user
"""
import os
import sys
import json
import shutil
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from utils.auth import get_password_hash

def reset_database():
    print("🔄 Réinitialisation de la base de données...")
    
    # Path to data directory
    data_dir = Path(__file__).parent / "data"
    
    # 1. Delete all JSON files
    print("\n📁 Suppression des fichiers de données...")
    json_files = [
        "users.json",
        "videos.json", 
        "clips.json",
        "subscriptions.json",
        "activation_codes.json",
        "verification_codes.json"
    ]
    
    for filename in json_files:
        filepath = data_dir / filename
        if filepath.exists():
            filepath.unlink()
            print(f"  ✅ Supprimé: {filename}")
    
    # 2. Delete all uploaded videos and clips
    print("\n📹 Suppression des vidéos et clips...")
    uploads_dir = data_dir / "uploads"
    clips_dir = data_dir / "clips"
    
    if uploads_dir.exists():
        shutil.rmtree(uploads_dir)
        print(f"  ✅ Dossier uploads supprimé")
    
    if clips_dir.exists():
        shutil.rmtree(clips_dir)
        print(f"  ✅ Dossier clips supprimé")
    
    # Recreate directories
    uploads_dir.mkdir(parents=True, exist_ok=True)
    clips_dir.mkdir(parents=True, exist_ok=True)
    
    # 3. Create new admin user
    print("\n👤 Création du compte administrateur...")
    
    admin_email = "admin@clipgenius.ai"
    admin_password = "Admin2024!"
    
    # Create users.json with admin
    users_data = {
        "users": [
            {
                "id": "admin-001",
                "email": admin_email,
                "password_hash": get_password_hash(admin_password),
                "plan": "agency",  # Premium plan
                "credits": -1,  # Unlimited credits
                "is_verified": True,
                "created_at": "2024-01-01T00:00:00",
                "stripe_customer_id": None
            }
        ]
    }
    
    users_file = data_dir / "users.json"
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ Utilisateur admin créé")
    
    # 4. Create subscription for admin
    subscriptions_data = {
        "subscriptions": [
            {
                "id": "sub-admin-001",
                "user_id": "admin-001",
                "plan": "agency",
                "status": "active",
                "stripe_subscription_id": None,
                "stripe_customer_id": None,
                "start_date": "2024-01-01T00:00:00",
                "renew_date": "2099-12-31T23:59:59",  # Infinite duration
                "amount": 0
            }
        ]
    }
    
    subs_file = data_dir / "subscriptions.json"
    with open(subs_file, 'w', encoding='utf-8') as f:
        json.dump(subscriptions_data, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ Abonnement premium illimité créé")
    
    # 5. Create empty files for other data
    for filename in ["videos.json", "clips.json", "activation_codes.json", "verification_codes.json"]:
        filepath = data_dir / filename
        if filename == "activation_codes.json":
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({"codes": []}, f, indent=2)
        elif filename == "verification_codes.json":
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({"codes": []}, f, indent=2)
        else:
            entity_type = filename.replace('.json', '')
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({entity_type: []}, f, indent=2)
        print(f"  ✅ Créé: {filename}")
    
    print("\n" + "="*60)
    print("✅ Base de données réinitialisée avec succès!")
    print("="*60)
    print("\n📋 INFORMATIONS DE CONNEXION:")
    print(f"   Email:    {admin_email}")
    print(f"   Password: {admin_password}")
    print(f"   Plan:     Agency (Premium)")
    print(f"   Credits:  ILLIMITÉS")
    print(f"   Durée:    INFINIE (jusqu'à 2099)")
    print("="*60)

if __name__ == "__main__":
    reset_database()
