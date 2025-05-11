import jwt
from fastapi import HTTPException, Request
from datetime import datetime, timedelta
import base64
import hmac
import hashlib
import json

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_token_from_request(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header. Expected: 'Bearer <token>'"
        )
    return auth_header.split(" ")[1].strip()


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    try:
        header_enc, payload_enc, signature_enc = token.split('.')

        signing_input = f"{header_enc}.{payload_enc}".encode()
        secret_key = SECRET_KEY.encode()
        expected_sig = base64.urlsafe_b64encode(
            hmac.new(secret_key, signing_input, hashlib.sha256).digest()
        ).decode().replace("=", "")

        if not hmac.compare_digest(signature_enc, expected_sig):
            raise HTTPException(status_code=401, detail="Invalid signature")

        payload = json.loads(base64.urlsafe_b64decode(payload_enc + "==").decode())

        if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
            raise HTTPException(status_code=401, detail="Token expired")

        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


def get_current_user(request: Request):
    token = get_token_from_request(request)
    return verify_token(token)