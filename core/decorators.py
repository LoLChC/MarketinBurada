from django.shortcuts import redirect
from functools import wraps
from account.models import User
from django.core.cache import cache

def required_login(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get("user-id")
        if not user_id:
            return redirect("account:login")
        
        
        user = cache.get(f"user-{user_id}")

        if not user:
            user = User.objects.filter(id=user_id).first()
            if user:
                cache.set(f"user-{user_id}", user, timeout=300)

        request.user_obj = user

        return view_func(request, *args, **kwargs)

    return wrapper

def required_logout(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get("user-id")
        if user_id:
            return redirect("account:user-account")

        return view_func(request, *args, **kwargs)

    return wrapper