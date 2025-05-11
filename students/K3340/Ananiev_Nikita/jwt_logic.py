from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError, jwt, ExpiredSignatureError
import datetime
from functools import wraps
from fastapi.security import  HTTPBearer

bearer_scheme = HTTPBearer()

class JWTAuth:
    def __init__(self, secret: str, hash_algo: str = "HS256", required_role: str = None):
        self.secret_key = secret
        self.hash_algo = hash_algo
        self.required_role = required_role

    def encode_token(self, profile_id: int) -> str:
        payload = {
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            "iat": datetime.datetime.utcnow(),
            "sub": str(profile_id),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.hash_algo)

    def decode_token(self, token: str) -> dict:
        try:
            print(type(token), self.secret_key)
            return jwt.decode(token, self.secret_key, algorithms=[self.hash_algo])
        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=401, detail="Invalid token")
        except BaseException:
            raise HTTPException(status_code=500, detail="Server error - can't decode token")

    def __call__(self, handler):
        @wraps(handler)
        async def wrapper(*args, **kwargs):
            creds: HTTPAuthorizationCredentials = kwargs.get("credentials")
            if not creds:
                raise HTTPException(status_code=401, detail="Missing or invalid token")

            token_val = creds.credentials
            token_data = self.decode_token(token_val)
            return await handler(*args, **kwargs)
        return wrapper
