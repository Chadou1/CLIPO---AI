import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from pathlib import Path

CODES_FILE = Path(__file__).parent / "activation_codes.json"

def load_codes() -> list:
    """Load activation codes from JSON file"""
    if not CODES_FILE.exists():
        return []
    
    with open(CODES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_codes(codes: list):
    """Save activation codes to JSON file"""
    with open(CODES_FILE, 'w', encoding='utf-8') as f:
        json.dump(codes, f, indent=2, ensure_ascii=False)

def validate_activation_code(code: str) -> Optional[Dict]:
    """
    Validate an activation code
    Returns the code data if valid, None otherwise
    """
    codes = load_codes()
    
    for code_data in codes:
        if code_data['code'] == code.upper():
            if code_data['used']:
                return {'error': 'Code already used', 'valid': False}
            
            # Check if code is still valid (not expired)
            created_at = datetime.fromisoformat(code_data['created_at'])
            # For now, codes don't expire, only get used once
            
            return {
                'valid': True,
                'duration_days': code_data['duration_days'],
                'code_data': code_data
            }
    
    return {'error': 'Invalid code', 'valid': False}

def use_activation_code(code: str, user_email: str) -> bool:
    """
    Mark an activation code as used
    Returns True if successful, False otherwise
    """
    codes = load_codes()
    
    for code_data in codes:
        if code_data['code'] == code.upper():
            if not code_data['used']:
                code_data['used'] = True
                code_data['used_by'] = user_email
                code_data['used_at'] = datetime.utcnow().isoformat()
                save_codes(codes)
                return True
            return False
    
    return False

def get_activation_expiry_date(duration_days: int) -> datetime:
    """Get the expiry date for an activation"""
    return datetime.utcnow() + timedelta(days=duration_days)

def generate_new_code(duration_days: int = 30) -> str:
    """
    Generate a new activation code
    Format: XXXX-XXXX-XXXX (12 characters)
    """
    import random
    import string
    
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choices(chars, k=12))
    formatted_code = f"{code[:4]}-{code[4:8]}-{code[8:12]}"
    
    codes = load_codes()
    codes.append({
        'code': formatted_code,
        'duration_days': duration_days,
        'used': False,
        'created_at': datetime.utcnow().isoformat(),
        'used_by': None,
        'used_at': None
    })
    save_codes(codes)
    
    return formatted_code

def get_unused_codes_count() -> int:
    """Get count of unused activation codes"""
    codes = load_codes()
    return sum(1 for code in codes if not code['used'])
