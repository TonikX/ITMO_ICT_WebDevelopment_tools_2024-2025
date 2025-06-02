import base64
import json
import hmac
import hashlib
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from db.connection import get_session
from models.models import User

SECRET_KEY = "mysecretkey"
security = HTTPBearer()


def encode_jwt(payload: dict) -> str:
    for key, value in payload.items():
        if isinstance(value, datetime):
            payload[key] = value.isoformat()

    header = {"alg": "HS256", "typ": "JWT"}
    header_encoded = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")

    signature_payload = f"{header_encoded}.{payload_encoded}"
    signature = hmac.new(SECRET_KEY.encode(), signature_payload.encode(), hashlib.sha256).digest()
    signature_encoded = base64.urlsafe_b64encode(signature).decode().rstrip("=")

    return f"{header_encoded}.{payload_encoded}.{signature_encoded}"


def decode_jwt(token: str) -> dict:
    try:
        header_encoded, payload_encoded, signature_encoded = token.split(".")
        signature_payload = f"{header_encoded}.{payload_encoded}"
        expected_signature = hmac.new(SECRET_KEY.encode(), signature_payload.encode(), hashlib.sha256).digest()
        signature = base64.urlsafe_b64decode(signature_encoded + "==")

        if not hmac.compare_digest(expected_signature, signature):
            raise HTTPException(status_code=401, detail="Invalid token signature")

        payload = json.loads(base64.urlsafe_b64decode(payload_encoded + "==").decode())

        if "exp" in payload and datetime.utcnow().timestamp() > float(payload["exp"]):
            raise HTTPException(status_code=401, detail="Token has expired")

        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        session: Session = Depends(get_session)
) -> User:
    token = credentials.credentials
    payload = decode_jwt(token)
    email = payload.get("sub")

    if not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = session.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
