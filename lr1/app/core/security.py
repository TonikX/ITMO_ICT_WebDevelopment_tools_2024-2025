import base64
import json
import hmac
import hashlib
import time
from typing import Dict, Any, Optional


SECRET_KEY = "blablabla2281337"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 3600


def generate_jwt(data: Dict[str, Any], expire: int = ACCESS_TOKEN_EXPIRE_SECONDS) -> str:
    header = {"alg": ALGORITHM, "typ": "JWT"}
    payload = data.copy()
    payload["exp"] = int(time.time()) + expire

    header_json = json.dumps(header, separators=(",", ":")).encode()
    payload_json = json.dumps(payload, separators=(",", ":")).encode()

    header_b64 = base64.urlsafe_b64encode(header_json).rstrip(b'=')
    payload_b64 = base64.urlsafe_b64encode(payload_json).rstrip(b'=')

    signature = hmac.new(SECRET_KEY.encode(), header_b64 + b'.' + payload_b64, hashlib.sha256).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).rstrip(b'=')

    token = header_b64.decode() + "." + payload_b64.decode() + "." + signature_b64.decode()
    return token


def verify_jwt(token: str) -> Optional[Dict[str, Any]]:
    try:
        header_b64, payload_b64, signature_b64 = token.split('.')
        signing_input = (header_b64 + "." + payload_b64).encode()
        expected_signature = hmac.new(SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
        expected_signature_b64 = base64.urlsafe_b64encode(expected_signature).rstrip(b'=')
        if expected_signature_b64.decode() != signature_b64:
            return None

        def add_padding(b64_string: str) -> str:
            return b64_string + '=' * (-len(b64_string) % 4)

        payload_json = base64.urlsafe_b64decode(add_padding(payload_b64)).decode()
        payload = json.loads(payload_json)
        if payload.get("exp", 0) < int(time.time()):
            return None
        return payload
    except Exception:
        return None


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed
