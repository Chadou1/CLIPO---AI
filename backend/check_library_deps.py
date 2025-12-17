#!/usr/bin/env python3
"""
Check if all required dependencies for library service are installed
"""

import sys

def check_dependencies():
    """Check if all required packages are available"""
    required = {
        'fastapi': 'FastAPI',
        'jose': 'python-jose[cryptography]',
        'bcrypt': 'bcrypt',
        'librosa': 'librosa',
        'moviepy.editor': 'moviepy',
        'scipy': 'scipy',
        'PIL': 'Pillow',
        'numpy': 'numpy',
        'yt_dlp': 'yt-dlp',
        'psutil': 'psutil',
        'pydantic': 'pydantic',
    }
    
    missing = []
    print("Checking library service dependencies...\n")
    
    for module, package in required.items():
        try:
            __import__(module)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing {len(missing)} package(s):")
        for pkg in missing:
            print(f"   - {pkg}")
        print(f"\nInstall with:")
        print(f"   pip install {' '.join(missing)}")
        return False
    else:
        print("\n✅ All dependencies installed!")
        return True

if __name__ == "__main__":
    success = check_dependencies()
    sys.exit(0 if success else 1)
