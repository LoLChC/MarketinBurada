from django.shortcuts import redirect
from django.http import JsonResponse
from django.shortcuts import render
from account.models import User
from .decorators import required_logout, required_login
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect
from account.models import Address
from .redis_client import redis_conf as redis
from . import tokens

# Create your views here.
def read_verify_email(request):
    token = request.GET.get("token")
    payload = tokens.decode_email_verify_token(token)

    if not payload:
        return redirect("account:verification-unsuccess")

    user_id = payload["user-id"]
    user = User.objects.filter(id=user_id).first()
    
    if user:
        user.email_verify = True
        user.save()
        session = tokens.generate_email_verify_session("True", user.id)
        str_id = str(user.id)
        key = f"email_verify:{str_id}"
        redis.set(
            key,
            "True",
            ex=300,
        )
        response = redirect("account:verification-success")
        response.set_cookie(
            "email_verify_session",
            session,
            httponly=True
        )
        return response
    
    else:
        return redirect("account:verification-unsuccess")

@required_login
def verify_email_looking(request):
    cookie_data = request.COOKIES.get('email_verify_session')
    
    if not cookie_data:
        user_id = str(request.user_obj.id)
        key = f"email_verify:{user_id}"
        code = redis.get(key)
        redis.delete(key)
        if code is None:
            return JsonResponse({"verify": False})
        
        
        answer = code

    else:
        payload = tokens.decode_email_verify_session(cookie_data)
        
        if not payload or payload.get("user_id") != request.user_obj.id:
            response = JsonResponse({"verify": False})
            response.delete_cookie("email_verify_session")
            return response
        
        answer = payload["answer"]

    if answer == "True":
        response = JsonResponse({"verify": True})
        response.delete_cookie("email_verify_session") 
        return response
    elif answer == "False":
        response = JsonResponse({"verify": False})
        response.delete_cookie("email_verify_session") 
        return response
    
    return JsonResponse({"verify": None})

@required_logout
def read_forgot_password(request):
    token = request.GET.get("code")
    payload = tokens.decode_forgot_password_token(token)

    str_token_email = str(payload["email"])

    key = f"email:{str_token_email}"
    str_redis_email = str(redis.get(key))

    if not payload:
        return redirect("account:forgot-password-unchange")
    
    if str_redis_email is None:
        return redirect("account:forgot-password-unchange")
    
    if str_redis_email == str_token_email:
        response = redirect("account:forgot-password-change")
        response.set_cookie(
            "password_reset_verified",
            "true",
            httponly=True,
            max_age=300
        )
        print(str_token_email)
        response.set_cookie(
            "token_email",
            str_token_email,
            httponly=True,
            max_age=300
        )
        return response
    else:
        return redirect("account:forgot-password-unchange")
    
def clear(request):
    response = redirect("account:login")

    request.session.flush()
    redis.flushdb()
    cache.clear()

    for cookie_name in request.COOKIES.keys():
            response.delete_cookie(
                key=cookie_name,
                path='/',
                domain=None
            )

    return response

@required_login
def address_delete(request, pk):
    if request.method == "POST":
        address = get_object_or_404(Address, id=pk, user=request.user_obj)
        address.delete()

    return redirect("account:user-account")

def trys(request):
    return render(request, 'core/try.html')