"""
Script d'installation automatique pour Clipo
Exécutez simplement: python setup.py
"""

import os
import sys
import subprocess
import shutil
import zipfile
import urllib.request
from pathlib import Path

def print_step(message):
    """Print a colored step message"""
    print(f"\n{'='*60}")
    print(f"🚀 {message}")
    print('='*60)

def run_command(command, cwd=None, shell=True):
    """Run a command and return success status"""
    try:
        # Convert Path objects to strings
        if cwd and isinstance(cwd, Path):
            cwd = str(cwd.absolute())
        
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=shell,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        return False, error_msg
    except Exception as e:
        return False, str(e)


def install_ffmpeg():
    """Download and install FFmpeg"""
    print_step("Installation de FFmpeg")
    
    # Get absolute paths
    script_dir = Path(__file__).parent.absolute()
    backend_dir = script_dir / "backend"
    ffmpeg_dir = backend_dir / "ffmpeg"
    
    # Create directory
    ffmpeg_dir.mkdir(parents=True, exist_ok=True)
    
    # URL for Windows build (GPL version)
    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    zip_path = ffmpeg_dir / "ffmpeg.zip"
    
    print(f"⬇️ Téléchargement de FFmpeg depuis {url}...")
    try:
        urllib.request.urlretrieve(url, zip_path)
        print("✅ Téléchargement terminé")
        
        print("📦 Extraction de l'archive...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(ffmpeg_dir)
        
        # Find bin directory
        bin_dir = None
        for root, dirs, files in os.walk(ffmpeg_dir):
            if "bin" in dirs:
                bin_dir = Path(root) / "bin"
                break
        
        if bin_dir and (bin_dir / "ffmpeg.exe").exists():
            print(f"✅ FFmpeg extrait dans: {bin_dir}")
            
            # Add to PATH for current session
            os.environ["PATH"] += os.pathsep + str(bin_dir)
            
            # Clean up zip
            zip_path.unlink()
            return True
        else:
            print("❌ Impossible de trouver le dossier bin de FFmpeg")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'installation de FFmpeg: {str(e)}")
        return False

def check_python_version():
    """Check if Python version is 3.11+"""
    print_step("Vérification de Python")
    version = sys.version_info
    # Allow Python 3.8+ instead of 3.11+ for broader compatibility
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ requis. Version actuelle: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_node():
    """Check if Node.js is installed"""
    print_step("Vérification de Node.js")
    success, output = run_command("node --version")
    if success:
        print(f"✅ Node.js {output.strip()}")
        return True
    print("❌ Node.js non installé. Téléchargez depuis: https://nodejs.org/")
    return False

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print_step("Vérification de FFmpeg")
    
    # First check
    success, output = run_command("ffmpeg -version")
    if success:
        print(f"✅ FFmpeg installé (Système)")
        return True
    
    # Check local installation
    script_dir = Path(__file__).parent.absolute()
    local_ffmpeg = script_dir / "backend" / "ffmpeg"
    
    # Find bin directory recursively
    bin_dir = None
    if local_ffmpeg.exists():
        for root, dirs, files in os.walk(local_ffmpeg):
            if "bin" in dirs:
                potential_bin = Path(root) / "bin"
                if (potential_bin / "ffmpeg.exe").exists():
                    bin_dir = potential_bin
                    break
    
    if bin_dir:
        print(f"✅ FFmpeg détecté localement: {bin_dir}")
        os.environ["PATH"] += os.pathsep + str(bin_dir)
        return True
        
    print("⚠️ FFmpeg non trouvé. Installation automatique...")
    if install_ffmpeg():
        # Verify again
        success, output = run_command("ffmpeg -version")
        if success:
            print("✅ FFmpeg installé et configuré avec succès!")
            return True
    
    print("❌ Échec de l'installation automatique de FFmpeg.")
    print("   Téléchargez manuellement depuis: https://ffmpeg.org/download.html")
    return False

def setup_backend():
    """Setup backend environment"""
    print_step("Configuration du Backend")
    
    # Get absolute paths
    script_dir = Path(__file__).parent.absolute()
    backend_dir = script_dir / "backend"
    venv_dir = backend_dir / "venv"
    
    print(f"📁 Répertoire backend: {backend_dir}")
    
    if not backend_dir.exists():
        print(f"❌ Le dossier backend n'existe pas: {backend_dir}")
        return False
    
    # Create virtual environment
    if not venv_dir.exists():
        print("📦 Création de l'environnement virtuel...")
        success, output = run_command(f'python -m venv "{venv_dir}"')
        if not success:
            print("❌ Échec de création du venv")
            print(output)
            return False
        print("✅ Environnement virtuel créé")
    else:
        print("✅ Environnement virtuel existant")
    
    # Determine pip path with absolute paths
    if os.name == 'nt':  # Windows
        pip_path = venv_dir / "Scripts" / "pip.exe"
        python_path = venv_dir / "Scripts" / "python.exe"
    else:
        pip_path = venv_dir / "bin" / "pip"
        python_path = venv_dir / "bin" / "python"
    
    print(f"📍 Pip: {pip_path}")
    if not pip_path.exists():
        print(f"❌ Pip non trouvé: {pip_path}")
        return False
    
    # Upgrade pip first
    print("📦 Mise à jour de pip...")
    success, output = run_command(f'"{python_path}" -m pip install --upgrade pip')
    if success:
        print("✅ Pip mis à jour")
    else:
        print("⚠️ Échec de mise à jour de pip, on continue...")
    
    # Install dependencies
    print("📦 Installation des dépendances Python...")
    requirements_file = backend_dir / "requirements.txt"
    minimal_requirements_file = backend_dir / "requirements-minimal.txt"
    
    if not requirements_file.exists():
        print(f"❌ Fichier requirements.txt non trouvé: {requirements_file}")
        return False
    
    print(f"📄 Fichier requirements.txt: {requirements_file}")
    
    # Use absolute paths for the command
    success, output = run_command(
        f'"{python_path}" -m pip install -r "{requirements_file}"',
        cwd=str(backend_dir)
    )
    
    if not success:
        print("❌ Échec d'installation des dépendances complètes")
        print("⚠️ Tentative avec les dépendances minimales...")
        
        # Try minimal requirements
        if minimal_requirements_file.exists():
            success, output = run_command(
                f'"{python_path}" -m pip install -r "{minimal_requirements_file}"',
                cwd=str(backend_dir)
            )
            if success:
                print("✅ Dépendances minimales installées")
                print("⚠️ Certaines fonctionnalités (AI, vidéo) ne seront pas disponibles")
                print("   Vous pouvez les installer plus tard avec:")
                print(f'   "{python_path}" -m pip install celery redis moviepy scenedetect[opencv] openai')
            else:
                print("❌ Échec d'installation des dépendances minimales")
                print(output)
                return False
        else:
            print(output)
            return False
    else:
        print("✅ Dépendances Python installées")
    
    # Create .env file
    env_example = backend_dir / ".env.example"
    env_file = backend_dir / ".env"
    
    if not env_file.exists() and env_example.exists():
        print("📝 Création du fichier .env...")
        shutil.copy(env_example, env_file)
        
        # Update .env with SQLite
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace(
            'DATABASE_URL=postgresql://clipgenius:password@localhost:5432/clipgenius',
            'DATABASE_URL=sqlite:///./clipgenius.db'
        )
        content = content.replace(
            'REDIS_URL=redis://localhost:6379/0',
            'REDIS_URL=redis://localhost:6379/0  # Optionnel pour démarrer'
        )
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fichier .env créé avec SQLite")
    
    # Initialize database
    print("🗄️ Initialisation de la base de données...")
    init_cmd = f'"{python_path}" -c "from models import init_db; init_db()"'
    success, output = run_command(init_cmd, cwd=str(backend_dir))
    if success:
        print("✅ Base de données initialisée")
    else:
        print("⚠️ La base sera créée au premier lancement")
    
    # Create storage directories
    storage_dir = backend_dir / "storage"
    for subdir in ["uploads", "clips", "temp"]:
        (storage_dir / subdir).mkdir(parents=True, exist_ok=True)
    print("✅ Dossiers de stockage créés")
    
    return True

def setup_frontend():
    """Setup frontend environment"""
    print_step("Configuration du Frontend")
    
    # Get absolute paths
    script_dir = Path(__file__).parent.absolute()
    frontend_dir = script_dir / "frontend"
    
    print(f"📁 Répertoire frontend: {frontend_dir}")
    
    if not frontend_dir.exists():
        print(f"❌ Le dossier frontend n'existe pas: {frontend_dir}")
        return False
    
    # Install npm dependencies
    print("📦 Installation des dépendances npm...")
    success, output = run_command("npm install", cwd=str(frontend_dir))
    if not success:
        print("❌ Échec d'installation npm")
        print(output)
        return False
    print("✅ Dépendances npm installées")
    
    # Create .env.local
    env_example = frontend_dir / ".env.local.example"
    env_file = frontend_dir / ".env.local"
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Fichier .env.local créé")
    elif not env_file.exists():
        # Create a default .env.local
        print("📝 Création d'un fichier .env.local par défaut...")
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("NEXT_PUBLIC_API_URL=http://localhost:32190\n")
        print("✅ Fichier .env.local créé par défaut")
    
    return True

def create_start_scripts():
    """Create scripts to start the application"""
    print_step("Création des scripts de lancement")
    
    # Windows batch script
    start_bat = """@echo off
echo Starting Clipo AI...
echo.

REM Start Auth Service
echo Starting Auth Service (Port 32190)...
start "Clipo Auth Service" cmd /k "cd backend && venv\\Scripts\\activate && uvicorn auth_service:app --reload --host 0.0.0.0 --port 32190"

timeout /t 2 /nobreak >nul

REM Start Video Service
echo Starting Video Service (Port 32191)...
start "Clipo Video Service" cmd /k "cd backend && venv\\Scripts\\activate && uvicorn video_service:app --reload --host 0.0.0.0 --port 32191"

timeout /t 2 /nobreak >nul

REM Start Library Service
echo Starting Library Service (Port 32189)...
start "Clipo Library Service" cmd /k "cd backend && venv\\Scripts\\activate && uvicorn library_service:app --reload --host 0.0.0.0 --port 32189"

timeout /t 2 /nobreak >nul

REM Start frontend
echo Starting Frontend (Port 32192)...
start "Clipo Frontend" cmd /k "cd frontend && npx next dev -H 0.0.0.0 -p 32192"

echo.
echo ========================================
echo Clipo AI lancé avec succès!
echo ========================================
echo Site Web: http://88.191.169.79:32192
echo Auth API: http://88.191.169.79:32190
echo Video API: http://88.191.169.79:32191
echo Library API: http://88.191.169.79:32189
echo ========================================
echo PORTS A OUVRIR: 32189, 32190, 32191, 32192
echo ========================================
echo.
echo Appuyez sur une touche pour quitter...
pause >nul
"""
    
    with open("START.bat", "w", encoding='utf-8') as f:
        f.write(start_bat)
    
    print("✅ Script START.bat créé")
    
    # Create Python launcher
    launcher_py = """
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
    print("\\n🔐 Démarrage du Service Auth/Billing (Port 32190)...")
    auth_cmd = f'start "Clipo Auth Service" cmd /k "cd /d "{backend_dir}" && "{python_path}" -m uvicorn auth_service:app --reload --host 0.0.0.0 --port 32190"'
    subprocess.Popen(auth_cmd, shell=True)
    
    time.sleep(2)

    # 2. Start Video Service
    print("\\n🎥 Démarrage du Service Vidéo/Clips (Port 32191)...")
    video_cmd = f'start "Clipo Video Service" cmd /k "cd /d "{backend_dir}" && "{python_path}" -m uvicorn video_service:app --reload --host 0.0.0.0 --port 32191"'
    subprocess.Popen(video_cmd, shell=True)
    
    time.sleep(2)
    
    # 3. Start Library Service
    print("\\n📚 Démarrage du Service Library (Port 32189)...")
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

    print("\\nAppuyez sur Ctrl+C pour quitter ce script (les serveurs resteront ouverts)...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\\n👋 Au revoir!")

if __name__ == "__main__":
    main()
"""
    
    with open("start.py", "w", encoding='utf-8') as f:
        f.write(launcher_py)
    
    print("✅ Script start.py créé")
    
    return True

def launch_servers():
    """Launch backend and frontend servers"""
    print_step("Lancement des serveurs")
    
    import webbrowser
    import time
    
    # Get absolute paths
    script_dir = Path(__file__).parent.absolute()
    backend_dir = script_dir / "backend"
    frontend_dir = script_dir / "frontend"
    
    if os.name == 'nt':  # Windows
        python_path = backend_dir / "venv" / "Scripts" / "python.exe"
    else:
        python_path = backend_dir / "venv" / "bin" / "python"
    
    print("🔐 Démarrage du Service Auth/Billing (Port 32190)...")
    auth_cmd = f'start "Clipo Auth Service" cmd /k "cd /d "{backend_dir}" && "{python_path}" -m uvicorn auth_service:app --reload --host 0.0.0.0 --port 32190"'
    subprocess.Popen(auth_cmd, shell=True)
    
    time.sleep(2)
    
    print("🎥 Démarrage du Service Vidéo/Clips (Port 32191)...")
    video_cmd = f'start "Clipo Video Service" cmd /k "cd /d "{backend_dir}" && "{python_path}" -m uvicorn video_service:app --reload --host 0.0.0.0 --port 32191"'
    subprocess.Popen(video_cmd, shell=True)
    
    time.sleep(2)
    
    print("📚 Démarrage du Service Library (Port 32189)...")
    library_cmd = f'start "Clipo Library Service" cmd /k "cd /d "{backend_dir}" && "{python_path}" -m uvicorn library_service:app --reload --host 0.0.0.0 --port 32189"'
    subprocess.Popen(library_cmd, shell=True)
    
    time.sleep(2)
    
    print("🌐 Démarrage du Frontend (Port 32192)...")
    frontend_cmd = f'start "Clipo Frontend" cmd /k "cd /d "{frontend_dir}" && npx next dev -H 0.0.0.0 -p 32192"'
    subprocess.Popen(frontend_cmd, shell=True)
    
    print("⏳ Attente du démarrage (5 secondes)...")
    time.sleep(5)
    
    print("\n" + "="*60)
    print("✅ Clipo AI est lancé!")
    print("="*60)
    print("📍 Accès Public:")
    print("   🌐 Site Web: http://88.191.169.79:32192")
    print("   🔐 Auth API: http://88.191.169.79:32190")
    print("   🎥 Video API: http://88.191.169.79:32191")
    print("   📚 Library API: http://88.191.169.79:32189")
    print("\n⚠️  PORTS A OUVRIR DANS VOTRE ROUTEUR:")
    print("   - Port 32189 (Library)")
    print("   - Port 32190 (Auth/Billing)")
    print("   - Port 32191 (Vidéo/Clips)")
    print("   - Port 32192 (Frontend)")
    print("="*60)
    
    # Open browser
    print("\n🌐 Ouverture du navigateur...")
    try:
        webbrowser.open("http://localhost:32192")
    except:
        print("⚠️ Impossible d'ouvrir le navigateur automatiquement")
    
    return True

def main():
    """Main setup function"""
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║         Clipo - Installation                      ║
    ║         Version Locale Gratuite                   ║
    ╚═══════════════════════════════════════════════════╝
    """)
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    if not check_node():
        print("\n⚠️ Node.js requis. Installez-le d'abord.")
        return False
    
    check_ffmpeg()  # Warning only
    
    # Setup
    if not setup_backend():
        print("\n❌ Échec de configuration du backend")
        return False
    
    if not setup_frontend():
        print("\n❌ Échec de configuration du frontend")
        return False
    
    create_start_scripts()
    
    print_step("✨ Installation Terminée!")
    
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║              Installation Réussie! ✅              ║
    ╚═══════════════════════════════════════════════════╝
    
    📋 CODES D'ACTIVATION DISPONIBLES:
    
    1. FREE-TRIAL-2024-A1B2
    2. PREMIUM-ACCESS-C3D4
    3. CLIPGENIUS-E5F6
    4. ACTIVATE-NOW-G7H8
    5. UNLOCK-POWER-I9J0
    
    🚀 L'APPLICATION VA SE LANCER AUTOMATIQUEMENT...
    
    📍 ACCÈS:
        Site Web: http://88.191.169.79:32192
        Auth API: http://88.191.169.79:32190
        Video API: http://88.191.169.79:32191
    
    ⚠️  PORTS A OUVRIR: 32190, 32191, 32192
    
    💡 PREMIÈRE UTILISATION:
        1. Créez un compte
        2. Utilisez un code d'activation
        3. Uploadez une vidéo
        4. Récupérez vos clips!
    
    ⚠️ NOTE: SQLite est utilisé par défaut (plus simple)
            Redis est optionnel pour démarrer
    
    ════════════════════════════════════════════════════
    """)
    
    # Ask if user wants to launch servers now
    try:
        response = input("\n🚀 Voulez-vous lancer les serveurs maintenant? (O/n): ").strip().lower()
        if response == '' or response == 'o' or response == 'oui' or response == 'y' or response == 'yes':
            launch_servers()
            print("\n✅ Les serveurs sont lancés!")
            print("📌 Pour arrêter, fermez les fenêtres de terminal ou utilisez Ctrl+C")
        else:
            print("\n💡 Pour lancer plus tard:")
            print("   - Exécutez: python start.py")
            print("   - Ou double-cliquez sur: START.bat")
    except KeyboardInterrupt:
        print("\n\n⚠️ Lancement annulé")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Installation interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

