from django.shortcuts import redirect
from functools import wraps
from account.models import User
from django.core.cache import cache
from . import tokens

def required_login(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        token = request.COOKIES.get('login_token')
        if not token:
            return redirect("account:login")

        decoded_token = tokens.decode_login_token(token)

        if not decoded_token:
            return redirect("account:login")
        
        user_id = decoded_token.get("user-id")
        cache_key = f"user-{user_id}"
        
        user = cache.get(cache_key)

        if not user:
            user = User.objects.filter(id=user_id).first()
            if user:
                cache.set(f"user-{user_id}", user, timeout=300)
            else:
                response = redirect("account:login")
                response.delete_cookie("token")
                return response
            
        request.user_obj = user

        return view_func(request, *args, **kwargs)

    return wrapper

def required_logout(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        token = request.COOKIES.get('login_token')
        if token:
            decoded = tokens.decode_login_token(token)
            if decoded:
                return redirect("account:user-account")
        return view_func(request, *args, **kwargs)
    return wrapper