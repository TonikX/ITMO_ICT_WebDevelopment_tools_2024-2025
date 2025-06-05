import os
import hmac
import hashlib
import base64
import json
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .models import User
from .database import get_session
from sqlmodel import Session, select

SECRET_KEY = os.getenv("JWT_SECRET", "CHANGE_ME")
ALGORITHM  = os.getenv("JWT_ALGORITHM", "HS256")
EXPIRE_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

security = HTTPBearer()


def hash_password(password: str) -> str:
    salt = SECRET_KEY.encode()
    return hashlib.sha256(salt + password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def create_access_token(data: dict) -> str:
    header = {"alg": ALGORITHM, "typ": "JWT"}
    payload = data.copy()
    exp = datetime.utcnow() + timedelta(minutes=EXPIRE_MIN)
    payload.update({"exp": exp.timestamp()})
    segments = []
    for part in (header, payload):
        json_part = json.dumps(part, separators=(",", ":"), sort_keys=True)
        b64 = base64.urlsafe_b64encode(json_part.encode()).rstrip(b"=")
        segments.append(b64)
    signing_input = b".".join(segments)
    signature = hmac.new(SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
    b64sig = base64.urlsafe_b64encode(signature).rstrip(b"=")
    return b".".join(segments + [b64sig]).decode()


def decode_token(token: str) -> dict:
    try:
        header_b64, payload_b64, sig_b64 = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}".encode()
        signature = base64.urlsafe_b64decode(sig_b64 + "==")
        expected = hmac.new(SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
        if not hmac.compare_digest(signature, expected):
            raise HTTPException(401, "Invalid signature")
        payload_json = base64.urlsafe_b64decode(payload_b64 + "==")
        data = json.loads(payload_json)
        if data.get("exp", 0) < datetime.utcnow().timestamp():
            raise HTTPException(401, "Token expired")
        return data
    except Exception:
        raise HTTPException(401, "Invalid token")


def get_current_user(
    cred: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    token = cred.credentials
    data = decode_token(token)
    user = session.exec(select(User).where(User.id == data.get("sub"))).first()
    if not user:
        raise HTTPException(401, "User not found")
    return user