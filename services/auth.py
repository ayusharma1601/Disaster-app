import hashlib
import hmac
import os
import secrets
from datetime import datetime, timezone, timedelta
from threading import RLock
from typing import Optional, Dict

_DEPLOYED = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
_PRODUCTION = os.environ.get("ENVIRONMENT", "").lower() == "production" or _DEPLOYED
_DEFAULT_SECRET = "disaster-intel-secret-key-dhemaji-2026"
_configured_secret = os.environ.get("DISASTER_APP_SECRET_KEY")
if _PRODUCTION and (not _configured_secret or _configured_secret == _DEFAULT_SECRET):
    raise RuntimeError("Set a unique DISASTER_APP_SECRET_KEY before running in production.")
SECRET_KEY = _configured_secret or _DEFAULT_SECRET

ACTIVE_TOKENS: Dict[str, Dict] = {}
_TOKEN_LOCK = RLock()


def hash_password(password: str) -> str:
    """Hash a password with a random salt using PBKDF2-HMAC-SHA256."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return f"{salt}:{key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against the stored salt:key format."""
    try:
        salt, key_hex = hashed_password.split(":", 1)
        new_key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100000)
        return hmac.compare_digest(new_key.hex(), key_hex)
    except (AttributeError, ValueError, TypeError):
        return False


def create_access_token(user_id: int, login_identifier: str, role: str, expires_hours: int = 12) -> str:
    """Create an in-memory session token with a bounded lifetime."""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_hours)
    with _TOKEN_LOCK:
        ACTIVE_TOKENS[token] = {
            "user_id": user_id,
            "login_identifier": login_identifier,
            "role": role,
            "expires_at": expires_at,
        }
    return token


def get_current_user_from_token(token: Optional[str]) -> Optional[Dict]:
    """Validate a token and return its user payload, or None if invalid/expired."""
    if not token:
        return None
    with _TOKEN_LOCK:
        session = ACTIVE_TOKENS.get(token)
        if not session:
            return None
        if datetime.now(timezone.utc) > session["expires_at"]:
            ACTIVE_TOKENS.pop(token, None)
            return None
        return session.copy()
