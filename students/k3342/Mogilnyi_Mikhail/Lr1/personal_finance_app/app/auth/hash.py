import hashlib

def get_password_hash(password: str) -> str:
    """Return the SHA-256 hash of the given password."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare a plaintext password with the hashed version."""
    return get_password_hash(plain_password) == hashed_password
