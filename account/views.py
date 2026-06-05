from django.shortcuts import render, redirect
import random
from .models import User
from core.utils import control_login
# Create your views here.

def login(request):
    random_number = random.randint(1, 2000)
    return render(request, 'account/login.html', {'random_number': random_number})

def register(request):
    random_number = random.randint(1, 2000)
    control_login(request)

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email").lower().strip()
        password = request.POST.get("password")

        if User.objects.filter(email=email).exists():
            return render(request, 'account/register.html', {'error': 'Bu email zaten kayıtlı.', 'random_number': random_number})

        user = User(name=name, email=email)
        user.password_hash(password)
        user.save()

        request.session["user-id"] = user.id

        return redirect("account:user-account")

    return render(request, 'account/register.html', {'random_number': random_number})

def user_account(request):
    random_number = random.randint(1, 2000)
    return render(request, 'account/user-account.html', {'random_number': random_number})

def market_account(request):
    random_number = random.randint(1, 2000)
    return render(request, 'account/market-account.html', {'random_number': random_number})

def forgot_password(request):
    random_number = random.randint(1, 2000)
    return render(request, 'account/forgot-password.html', {'random_number': random_number})

def terms(request):
    random_number = random.randint(1, 2000)
    return render(request, 'account/terms.html', {'random_number': random_number})

def kvkk(request):
    random_number = random.randint(1, 2000)
    return render(request, 'account/kvkk.html', {'random_number': random_number})