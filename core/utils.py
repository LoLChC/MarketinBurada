from dotenv import load_dotenv
from django.core.mail import send_mail
from MarketinBurada import settings
from django.core.mail import EmailMultiAlternatives
from markets.models import Market
from django.core.cache import cache
from . import tokens
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta

load_dotenv()

def login(request, user, go, duration_days=None):
    response = redirect(go)
    token = tokens.generate_login_token(user)

    if duration_days:
        times = timezone.now() + timedelta(days=duration_days)
        response.set_cookie(
            "token",
            token,
            httponly=True,
            expires=times
        )
    else:
        response.set_cookie(
            "token",
            token,
            httponly=True
        )
    request.session.flush()
    request.session.cycle_key()

    return response

def logout():
    response = redirect("account:login")
    response.delete_cookie("token") 
    return response

def login_token_to_user_id(request):
    token = request.COOKIES.get('token')
    decoded_token = tokens.decode_login_token(token)
    user_id = decoded_token.get("user-id")
    return user_id
    

def send_mail_text(subject, message, to_email):
    if isinstance(to_email, str):
        to_email = [to_email]
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER, 
        recipient_list=to_email,
        fail_silently=False,
    )

def send_mail_html(subject, message, to_email):
    if isinstance(to_email, str):
        to_email = [to_email]

    email = EmailMultiAlternatives(
        subject=subject,
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        to=to_email
    )

    email.attach_alternative(message, "text/html")
    email.send()



def home_market_cache():
    key = "home-markets"

    market = cache.get(key)
    if market is not None:
        return market

    market = Market.objects.filter(status=True, home=True)
    cache.set(key, market, timeout=60 * 60 * 24 * 7)  # 1 hafta
    
    return market

def auth_state(request):
    return {
        "auth_state": bool(request.session.get("user-id"))
    }