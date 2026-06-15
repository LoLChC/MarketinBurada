from MarketinBurada.settings import SECRET_KEY
from datetime import datetime, timedelta, timezone
import hashlib
import secrets
import uuid
import time
import jwt

def generate_slug():
    t = str(time.time_ns())
    u = uuid.uuid4().hex
    r = secrets.token_hex(16)

    raw = f"{t}-{u}-{r}".encode()
    slug = hashlib.sha256(raw).hexdigest()[:24]

    return slug

def generate_forgot_password_token():
    return secrets.token_urlsafe(32)

def generate_login_token(user):
    payload = {
        "user-id": user.id,
        "email": user.email,
        "exp": datetime.now(timezone.utc) + timedelta(days=30)
    }

    token = jwt.encode(                
        payload,
        SECRET_KEY,
        algorithm="HS256"
    )

    return token

def decode_login_token(token):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None