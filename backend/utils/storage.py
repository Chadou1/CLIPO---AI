import os
import shutil
from datetime import datetime
from typing import BinaryIO

# Local storage directory
STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'storage')
UPLOADS_DIR = os.path.join(STORAGE_DIR, 'uploads')
CLIPS_DIR = os.path.join(STORAGE_DIR, 'clips')

# Create directories if they don't exist
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(CLIPS_DIR, exist_ok=True)

def upload_file_to_local(file: BinaryIO, filename: str, folder: str = "uploads") -> str:
    """Upload a file to local storage and return the file path"""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{filename}"
    
    # Determine folder path
    if folder == "uploads":
        folder_path = UPLOADS_DIR
    elif folder == "clips":
        folder_path = CLIPS_DIR
    else:
        folder_path = os.path.join(STORAGE_DIR, folder)
        os.makedirs(folder_path, exist_ok=True)
    
    file_path = os.path.join(folder_path, safe_filename)
    
    # Save file
    with open(file_path, 'wb') as f:
        shutil.copyfileobj(file, f)
    
    return file_path

def upload_file_path_to_local(source_path: str, filename: str, folder: str = "clips") -> str:
    """Copy a local file to storage folder"""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{filename}"
    
    if folder == "clips":
        folder_path = CLIPS_DIR
    else:
        folder_path = os.path.join(STORAGE_DIR, folder)
        os.makedirs(folder_path, exist_ok=True)
    
    dest_path = os.path.join(folder_path, safe_filename)
    shutil.copy2(source_path, dest_path)
    
    return dest_path

def get_file_url(file_path: str) -> str:
    """Get URL for a file (for local storage, return the file path)"""
    # In a production environment, this would return a proper URL
    # For local dev, we return the absolute path
    return os.path.abspath(file_path)

def delete_file_from_local(file_path: str):
    """Delete a file from local storage"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Failed to delete file: {str(e)}")

def get_storage_stats() -> dict:
    """Get storage statistics"""
    total_size = 0
    file_count = 0
    
    for folder in [UPLOADS_DIR, CLIPS_DIR]:
        for root, dirs, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
                file_count += 1
    
    return {
        'total_size_mb': round(total_size / (1024 * 1024), 2),
        'file_count': file_count,
        'uploads_dir': UPLOADS_DIR,
        'clips_dir': CLIPS_DIR
    }

# Compatibility aliases for S3 function names
upload_file_to_s3 = upload_file_to_local
upload_file_path_to_s3 = upload_file_path_to_local
get_presigned_url = get_file_url
delete_file_from_s3 = delete_file_from_local
