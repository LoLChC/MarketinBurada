import uuid
import time
import secrets
import hashlib

def generate_slug():
    t = str(time.time_ns())
    u = uuid.uuid4().hex
    r = secrets.token_hex(16)

    raw = f"{t}-{u}-{r}".encode()
    slug = hashlib.sha256(raw).hexdigest()[:24]

    return slug

def generate_forgot_password_token():
    return secrets.token_urlsafe(32)