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