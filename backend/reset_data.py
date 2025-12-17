"""
Script de reset des données ClipGenius

Reset les dossiers et fichiers JSON tout en préservant users.json
"""

import os
import shutil
import json
import sys
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def reset_data():
    """Reset tous les dossiers et fichiers JSON sauf users.json"""
    
    print("="*60)
    print("🔄 RESET DES DONNÉES CLIPGENIUS")
    print("="*60)
    
    # Chemin du dossier storage
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    storage_dir = os.path.join(backend_dir, "storage")
    
    print(f"\n📁 Storage directory: {storage_dir}")
    
    # 1. Reset des dossiers
    folders_to_reset = ["clips", "uploads", "temp"]
    
    print("\n🗑️  Suppression des dossiers...")
    for folder_name in folders_to_reset:
        folder_path = os.path.join(storage_dir, folder_name)
        
        if os.path.exists(folder_path):
            try:
                # Supprimer le dossier et tout son contenu
                shutil.rmtree(folder_path)
                print(f"   ✅ Supprimé: {folder_name}/")
                
                # Recréer le dossier vide
                os.makedirs(folder_path, exist_ok=True)
                print(f"   ✅ Recréé: {folder_name}/")
                
            except Exception as e:
                print(f"   ❌ Erreur avec {folder_name}/: {e}")
        else:
            # Créer le dossier s'il n'existe pas
            os.makedirs(folder_path, exist_ok=True)
            print(f"   ✅ Créé: {folder_name}/")
    
    # 2. Reset des fichiers JSON
    json_files_to_reset = {
        "clips.json": [],
        "credit_logs.json": [],
        "videos.json": []
    }
    
    print("\n📄 Reset des fichiers JSON...")
    for filename, default_content in json_files_to_reset.items():
        file_path = os.path.join(storage_dir, filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_content, f, indent=2)
            print(f"   ✅ Reset: {filename} → {default_content}")
            
        except Exception as e:
            print(f"   ❌ Erreur avec {filename}: {e}")
    
    # 3. Vérifier que users.json est préservé
    users_file = os.path.join(storage_dir, "users.json")
    
    print("\n👥 Vérification de users.json...")
    if os.path.exists(users_file):
        try:
            with open(users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            user_count = len(users_data) if isinstance(users_data, list) else 0
            print(f"   ✅ Préservé: users.json ({user_count} utilisateurs)")
            
        except Exception as e:
            print(f"   ⚠️ Erreur de lecture users.json: {e}")
    else:
        print(f"   ⚠️ users.json n'existe pas")
    
    # 4. Résumé
    print("\n" + "="*60)
    print("✅ RESET TERMINÉ")
    print("="*60)
    print("\nRésumé:")
    print("  • Dossiers vidés: clips/, uploads/, temp/")
    print("  • JSON reset: clips.json, credit_logs.json, videos.json")
    print("  • Préservé: users.json")
    print("\n💡 Vous pouvez maintenant redémarrer les services.")
    print("="*60)


if __name__ == "__main__":
    import sys
    
    # Demander confirmation
    print("\n⚠️  ATTENTION: Cette opération va supprimer:")
    print("   • Toutes les vidéos dans uploads/")
    print("   • Tous les clips dans clips/")
    print("   • Tous les fichiers temporaires dans temp/")
    print("   • Toutes les données de clips.json, videos.json, credit_logs.json")
    print("\n✅ Les utilisateurs (users.json) seront PRÉSERVÉS")
    
    response = input("\n❓ Voulez-vous continuer? (oui/non): ").strip().lower()
    
    if response in ['oui', 'yes', 'y', 'o']:
        reset_data()
    else:
        print("\n❌ Opération annulée.")
        sys.exit(0)
