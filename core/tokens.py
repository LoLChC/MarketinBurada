from MarketinBurada.settings import SECRET_KEY, EMAIL_VERIFY_KEY, FORGOT_PASSWORD_KEY
from datetime import datetime, timedelta, timezone
import secrets
import jwt

def generate_email_verify_token(user):
    payload = {
        "user-id": user.id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }

    token = jwt.encode(                
        payload,
        EMAIL_VERIFY_KEY,
        algorithm="HS256"
    )

    return token

def decode_email_verify_token(token):
    try:
        payload = jwt.decode(
            token,
            EMAIL_VERIFY_KEY,
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    
def generate_email_verify_session(answer, user_id):
    payload = {
        "user_id" : user_id,
        "answer": answer,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }

    token = jwt.encode(                
        payload,
        EMAIL_VERIFY_KEY,
        algorithm="HS256"
    )

    return token

def decode_email_verify_session(token):
    try:
        payload = jwt.decode(
            token,
            EMAIL_VERIFY_KEY,
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    

def generate_forgot_password_token(email):
    payload = {
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }

    token = jwt.encode(                
        payload,
        FORGOT_PASSWORD_KEY,
        algorithm="HS256"
    )

    return token

def decode_forgot_password_token(token):
    try:
        payload = jwt.decode(
            token,
            FORGOT_PASSWORD_KEY,
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

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