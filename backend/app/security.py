import base64
import hashlib
from cryptography.fernet import Fernet
from app.config import ENCRYPTION_KEY

def _get_fernet():
    key_bytes = hashlib.sha256(ENCRYPTION_KEY.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    return Fernet(fernet_key)

def encrypt_secret(plain_text: str) -> str:
    if not plain_text:
        return ""
    f = _get_fernet()
    return f.encrypt(plain_text.encode()).decode()

def decrypt_secret(cipher_text: str) -> str:
    if not cipher_text:
        return ""
    try:
        f = _get_fernet()
        return f.decrypt(cipher_text.encode()).decode()
    except Exception:
        return ""

def mask_secret(value: str) -> str:
    if not value or len(value) < 6:
        return "••••••••"
    return value[:3] + "••••" + value[-3:]
