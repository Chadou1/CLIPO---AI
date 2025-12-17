
import subprocess
import time
import webbrowser
import os
import sys

def main():
    print("🚀 Lancement de Clipo AI...")
    
    # Get absolute paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(script_dir, "backend")
    frontend_dir = os.path.join(script_dir, "frontend")
    
    # Determine python path in venv
    if os.name == 'nt':  # Windows
        python_path = os.path.join(backend_dir, "venv", "Scripts", "python.exe")
    else:
        python_path = os.path.join(backend_dir, "venv", "bin", "python")
        
    if not os.path.exists(python_path):
        print(f"❌ Environnement virtuel non trouvé: {python_path}")
        print("Veuillez exécuter setup.py d'abord.")
        input("Appuyez sur Entrée pour quitter...")
        return

    # 1. Start Auth Service
    print("\n🔐 Démarrage du Service Auth/Billing (Port 32190)...")
    auth_cmd = f'start "Clipo Auth Service" cmd /k "cd /d "{backend_dir}" && "{python_path}" -m uvicorn auth_service:app --reload --host 0.0.0.0 --port 32190"'
    subprocess.Popen(auth_cmd, shell=True)
    
    time.sleep(2)

    # 2. Start Video Service
    print("\n🎥 Démarrage du Service Vidéo/Clips (Port 32191)...")
    video_cmd = f'start "Clipo Video Service" cmd /k "cd /d "{backend_dir}" && "{python_path}" -m uvicorn video_service:app --reload --host 0.0.0.0 --port 32191"'
    subprocess.Popen(video_cmd, shell=True)
    
    time.sleep(2)
    
    # 3. Start Library Service
    print("\n📚 Démarrage du Service Library (Port 32189)...")
    library_cmd = f'start "Clipo Library Service" cmd /k "cd /d "{backend_dir}" && "{python_path}" -m uvicorn library_service:app --reload --host 0.0.0.0 --port 32189"'
    subprocess.Popen(library_cmd, shell=True)
    
    time.sleep(2)
    
    print("="*60)
    print("🌐 Site Web: http://88.191.169.79:32192")
    print("🔐 Auth API: http://88.191.169.79:32190")
    print("🎥 Video API: http://88.191.169.79:32191")
    print("📚 Library API: http://88.191.169.79:32189")
    print("="*60)
    print("⚠️  PORTS A OUVRIR: 32189, 32190, 32191, 32192")
    print("="*60)

    # Open browser
    try:
        webbrowser.open("http://localhost:3000")
    except:
        pass

    print("\nAppuyez sur Ctrl+C pour quitter ce script (les serveurs resteront ouverts)...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Au revoir!")

if __name__ == "__main__":
    main()
