import jwt
import datetime

payload = {
    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
    'iat': datetime.datetime.utcnow(),
    'sub': '123'
}

secret = 'test_secret'

token = jwt.encode(payload, secret, algorithm='HS256')
print("JWT token:", token)
