from django.shortcuts import redirect
from django.http import JsonResponse
from django.shortcuts import render
from account.models import User
from .decorators import required_logout, required_login
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect
from account.models import Address


# Create your views here.

def read_verify_email(request):
    real_token = request.session.get("token")
    user_token = request.GET.get("token")
    user_id = request.session.get("user-id")

    if real_token == user_token:
        user = User.objects.filter(id=user_id).first()
        user.email_verify = True
        user.save()
        return redirect("account:verification-success")
    else:
        return redirect("account:verification-unsuccess")

def verify_email_looking(request):
    user_id = request.session.get("user-id")
    user = User.objects.filter(id=user_id).first()
    verify = user.email_verify
    if verify == True:
        ok = True
    else:
        ok = False

    return JsonResponse({"verify": ok})

@required_logout
def read_forgot_password(request):
    real_code = request.session.get("code")
    user_code = request.GET.get("code")

    if real_code and real_code == user_code:
        request.session['password-reset-verified'] = True
        del request.session["code"]
        return redirect("account:forgot-password-change")
    else:
        return redirect("account:forgot-password-unchange")
    
def clear_cache(request):
    cache.clear()
    return redirect("account:login")

@required_login
def address_delete(request, pk):
    if request.method == "POST":
        address = get_object_or_404(Address, id=pk, user=request.user_obj)
        address.delete()

    return redirect("account:user-account")

def trys(request):
    return render(request, 'core/try.html')