import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import threading
from pathlib import Path

class JSONStorage:
    """Thread-safe JSON file storage system"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.lock = threading.Lock()
        
        # Initialize data files
        # Use 'storage' directory instead of 'data'
        self.storage_dir = Path("storage")
        self.storage_dir.mkdir(exist_ok=True)
        
        # Subdirectories
        (self.storage_dir / "clips").mkdir(exist_ok=True)
        (self.storage_dir / "temp").mkdir(exist_ok=True)
        (self.storage_dir / "uploads").mkdir(exist_ok=True)
        
        self.files = {
            "users": self.storage_dir / "users.json",
            "videos": self.storage_dir / "videos.json",
            "clips": self.storage_dir / "clips.json",
            "subscriptions": self.storage_dir / "subscriptions.json",
            "credit_logs": self.storage_dir / "credit_logs.json"
        }
        
        # Create empty files if they don't exist
        for file_path in self.files.values():
            if not file_path.exists():
                self._write_json(file_path, [])
    
    def _read_json(self, file_path: Path) -> List[Dict]:
        """Read JSON file with thread safety"""
        with self.lock:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
    
    def _write_json(self, file_path: Path, data: List[Dict]):
        """Write JSON file with thread safety"""
        with self.lock:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    def _get_next_id(self, data: List[Dict]) -> int:
        """Get next available ID"""
        if not data:
            return 1
        return max(item.get('id', 0) for item in data) + 1
    
    # Users
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        users = self._read_json(self.files["users"])
        return next((u for u in users if u.get('email') == email), None)
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        users = self._read_json(self.files["users"])
        return next((u for u in users if u.get('id') == user_id), None)
    
    def create_user(self, user_data: Dict) -> Dict:
        """Create new user"""
        users = self._read_json(self.files["users"])
        user_data['id'] = self._get_next_id(users)
        user_data['created_at'] = datetime.utcnow().isoformat()
        users.append(user_data)
        self._write_json(self.files["users"], users)
        return user_data
    
    def update_user(self, user_id: int, updates: Dict) -> Optional[Dict]:
        """Update user"""
        users = self._read_json(self.files["users"])
        for i, user in enumerate(users):
            if user.get('id') == user_id:
                users[i].update(updates)
                self._write_json(self.files["users"], users)
                return users[i]
        return None
    
    def store_verification_code(self, email: str, code: str) -> bool:
        """Store email verification code with expiry (10 minutes)"""
        from datetime import datetime, timedelta
        users = self._read_json(self.files["users"])
        for i, user in enumerate(users):
            if user.get('email') == email:
                users[i]['verification_code'] = code
                users[i]['verification_code_expiry'] = (datetime.utcnow() + timedelta(minutes=10)).isoformat()
                self._write_json(self.files["users"], users)
                return True
        return False
    
    def verify_email_code(self, email: str, code: str) -> bool:
        """Verify email code and mark email as verified"""
        from datetime import datetime
        users = self._read_json(self.files["users"])
        for i, user in enumerate(users):
            if user.get('email') == email:
                # Check if code matches
                if user.get('verification_code') != code:
                    return False
                # Check if code expired
                expiry_str = user.get('verification_code_expiry')
                if expiry_str:
                    expiry = datetime.fromisoformat(expiry_str)
                    if datetime.utcnow() > expiry:
                        return False
                # Mark email as verified
                users[i]['email_verified'] = True
                users[i]['verification_code'] = None
                users[i]['verification_code_expiry'] = None
                self._write_json(self.files["users"], users)
                return True
        return False
    
    def store_reset_code(self, email: str, code: str) -> bool:
        """Store password reset code with expiry (10 minutes)"""
        from datetime import datetime, timedelta
        users = self._read_json(self.files["users"])
        for i, user in enumerate(users):
            if user.get('email') == email:
                users[i]['reset_code'] = code
                users[i]['reset_code_expiry'] = (datetime.utcnow() + timedelta(minutes=10)).isoformat()
                self._write_json(self.files["users"], users)
                return True
        return False
    
    def verify_reset_code(self, email: str, code: str) -> bool:
        """Verify password reset code"""
        from datetime import datetime
        users = self._read_json(self.files["users"])
        for user in users:
            if user.get('email') == email:
                if user.get('reset_code') != code:
                    return False
                expiry_str = user.get('reset_code_expiry')
                if expiry_str:
                    expiry = datetime.fromisoformat(expiry_str)
                    if datetime.utcnow() > expiry:
                        return False
                return True
        return False
    
    def clear_reset_code(self, email: str) -> bool:
        """Clear password reset code after use"""
        users = self._read_json(self.files["users"])
        for i, user in enumerate(users):
            if user.get('email') == email:
                users[i]['reset_code'] = None
                users[i]['reset_code_expiry'] = None
                self._write_json(self.files["users"], users)
                return True
        return False
    
    # Videos
    def get_videos_by_user(self, user_id: int) -> List[Dict]:
        """Get all videos for a user"""
        videos = self._read_json(self.files["videos"])
        return [v for v in videos if v.get('user_id') == user_id]
    
    def get_video_by_id(self, video_id: int) -> Optional[Dict]:
        """Get video by ID"""
        videos = self._read_json(self.files["videos"])
        return next((v for v in videos if v.get('id') == video_id), None)
    
    def create_video(self, video_data: Dict) -> Dict:
        """Create new video"""
        videos = self._read_json(self.files["videos"])
        video_data['id'] = self._get_next_id(videos)
        video_data['created_at'] = datetime.utcnow().isoformat()
        videos.append(video_data)
        self._write_json(self.files["videos"], videos)
        return video_data
    
    def update_video(self, video_id: int, updates: Dict) -> Optional[Dict]:
        """Update video"""
        videos = self._read_json(self.files["videos"])
        for i, video in enumerate(videos):
            if video.get('id') == video_id:
                videos[i].update(updates)
                self._write_json(self.files["videos"], videos)
                return videos[i]
        return None

    def update_video_status(self, video_id: int, status: str) -> Optional[Dict]:
        """Update video status"""
        return self.update_video(video_id, {"status": status})
    
    def delete_video(self, video_id: int) -> bool:
        """Delete video"""
        videos = self._read_json(self.files["videos"])
        filtered = [v for v in videos if v.get('id') != video_id]
        if len(filtered) < len(videos):
            self._write_json(self.files["videos"], filtered)
            # Also delete associated clips
            self.delete_clips_by_video(video_id)
            return True
        return False
    
    # Clips
    def get_clips_by_video(self, video_id: int) -> List[Dict]:
        """Get all clips for a video"""
        clips = self._read_json(self.files["clips"])
        return [c for c in clips if c.get('video_id') == video_id]
    
    def get_clip_by_id(self, clip_id: int) -> Optional[Dict]:
        """Get clip by ID"""
        clips = self._read_json(self.files["clips"])
        return next((c for c in clips if c.get('id') == clip_id), None)
    
    def create_clip(self, clip_data: Dict) -> Dict:
        """Create new clip"""
        clips = self._read_json(self.files["clips"])
        clip_data['id'] = self._get_next_id(clips)
        clip_data['created_at'] = datetime.utcnow().isoformat()
        clips.append(clip_data)
        self._write_json(self.files["clips"], clips)
        return clip_data
    
    def update_clip(self, clip_id: int, updates: Dict) -> Optional[Dict]:
        """Update clip"""
        clips = self._read_json(self.files["clips"])
        for i, clip in enumerate(clips):
            if clip.get('id') == clip_id:
                clips[i].update(updates)
                self._write_json(self.files["clips"], clips)
                return clips[i]
        return None
    
    def delete_clip(self, clip_id: int) -> bool:
        """Delete clip"""
        clips = self._read_json(self.files["clips"])
        filtered = [c for c in clips if c.get('id') != clip_id]
        if len(filtered) < len(clips):
            self._write_json(self.files["clips"], filtered)
            return True
        return False
    
    def delete_clips_by_video(self, video_id: int):
        """Delete all clips for a video"""
        clips = self._read_json(self.files["clips"])
        filtered = [c for c in clips if c.get('video_id') != video_id]
        self._write_json(self.files["clips"], filtered)
    
    # Subscriptions
    def get_subscription_by_user(self, user_id: int) -> Optional[Dict]:
        """Get subscription for a user"""
        subscriptions = self._read_json(self.files["subscriptions"])
        return next((s for s in subscriptions if s.get('user_id') == user_id), None)
    
    def create_subscription(self, subscription_data: Dict) -> Dict:
        """Create new subscription"""
        subscriptions = self._read_json(self.files["subscriptions"])
        subscription_data['id'] = self._get_next_id(subscriptions)
        subscription_data['created_at'] = datetime.utcnow().isoformat()
        subscriptions.append(subscription_data)
        self._write_json(self.files["subscriptions"], subscriptions)
        return subscription_data
    
    def update_subscription(self, subscription_id: int, updates: Dict) -> Optional[Dict]:
        """Update subscription"""
        subscriptions = self._read_json(self.files["subscriptions"])
        for i, sub in enumerate(subscriptions):
            if sub.get('id') == subscription_id:
                subscriptions[i].update(updates)
                self._write_json(self.files["subscriptions"], subscriptions)
                return subscriptions[i]
        return None
    
    # Credit Logs
    def get_credit_logs_by_user(self, user_id: int) -> List[Dict]:
        """Get all credit logs for a user"""
        logs = self._read_json(self.files["credit_logs"])
        return [l for l in logs if l.get('user_id') == user_id]
    
    def create_credit_log(self, log_data: Dict) -> Dict:
        """Create new credit log"""
        logs = self._read_json(self.files["credit_logs"])
        log_data['id'] = self._get_next_id(logs)
        log_data['created_at'] = datetime.utcnow().isoformat()
        logs.append(log_data)
        self._write_json(self.files["credit_logs"], logs)
        return log_data


# Global storage instance
_storage_instance = None

def get_storage() -> JSONStorage:
    """Get global storage instance"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = JSONStorage()
    return _storage_instance
