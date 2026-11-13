import hashlib
import hmac
import os
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict

SECRET_KEY = os.environ.get("DISASTER_APP_SECRET_KEY", "disaster-intel-secret-key-dhemaji-2026")
ACTIVE_TOKENS: Dict[str, Dict] = {}

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with a unique salt."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}:{key.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against salt:key hash format."""
    try:
        salt, key_hex = hashed_password.split(":")
        new_key = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return hmac.compare_digest(new_key.hex(), key_hex)
    except Exception:
        return False

def create_access_token(user_id: int, login_identifier: str, role: str, expires_hours: int = 12) -> str:
    """Generate a secure session token stored in memory."""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_hours)
    ACTIVE_TOKENS[token] = {
        "user_id": user_id,
        "login_identifier": login_identifier,
        "role": role,
        "expires_at": expires_at
    }
    return token

def get_current_user_from_token(token: Optional[str]) -> Optional[Dict]:
    """Validate a token and return user payload or None."""
    if not token or token not in ACTIVE_TOKENS:
        return None
    session = ACTIVE_TOKENS[token]
    if datetime.now(timezone.utc) > session["expires_at"]:
        del ACTIVE_TOKENS[token]
        return None
    return session
