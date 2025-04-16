import base64
import json
import time
import hmac
import hashlib
from datetime import timedelta, datetime
from typing import Dict, Any

SECRET_KEY = "your-secret-key"  # In production, use environment variables.
ALGORITHM = "HS256"

def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def create_access_token(data: Dict[str, Any], expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": int(expire.timestamp())})
    
    header = {"alg": ALGORITHM, "typ": "JWT"}
    header_enc = _base64url_encode(json.dumps(header).encode('utf-8'))
    payload_enc = _base64url_encode(json.dumps(to_encode).encode('utf-8'))
    
    signature_data = f"{header_enc}.{payload_enc}".encode('utf-8')
    signature = hmac.new(SECRET_KEY.encode('utf-8'), signature_data, hashlib.sha256).digest()
    signature_enc = _base64url_encode(signature)
    
    jwt_token = f"{header_enc}.{payload_enc}.{signature_enc}"
    return jwt_token

def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        header_enc, payload_enc, signature_enc = token.split(".")
        signature_data = f"{header_enc}.{payload_enc}".encode('utf-8')
        expected_signature = hmac.new(SECRET_KEY.encode('utf-8'), signature_data, hashlib.sha256).digest()
        expected_signature_enc = _base64url_encode(expected_signature)
        
        if not hmac.compare_digest(expected_signature_enc, signature_enc):
            raise ValueError("Invalid token signature")
        
        payload_bytes = base64.urlsafe_b64decode(payload_enc + "==")
        payload = json.loads(payload_bytes.decode('utf-8'))
        
        if payload.get("exp") < int(time.time()):
            raise ValueError("Token has expired")
        return payload
    except Exception as e:
        raise ValueError("Invalid token") from e
