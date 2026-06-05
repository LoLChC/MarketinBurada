from django.shortcuts import render, redirect
import random
from .models import User
from django.contrib.auth.hashers import check_password, make_password
from core.decorators import required_login, required_logout
from django.db.models import Q

# Create your views here.

@required_logout
def login(request):
    random_number = random.randint(1, 2000)

    if request.method == "POST":
        username_or_email = request.POST.get("username-or-email")
        password = request.POST.get("password")

        value = username_or_email.strip()
        user = User.objects.filter(Q(email=value.lower()) | Q(name=value)).first()

        if not user:
            return render(request, 'account/login.html', {'error': 'Kullanıcı adı veya email hatalı.','random_number': random_number})

        if not user.password_check(password):
            return render(request, 'account/login.html', {'error': 'Hatalı şifre.','random_number': random_number})
        
        request.session["user-id"] = user.id
        return redirect("account:user-account")

    return render(request, 'account/login.html', {'random_number': random_number})

@required_logout
def register(request):
    random_number = random.randint(1, 2000)

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email").lower().strip()
        password = request.POST.get("password")

        if User.objects.filter(email=email).exists():
            return render(request, 'account/register.html', {'error': 'Bu email zaten kayıtlı.', 'random_number': random_number})

        user = User(name=name, email=email)
        user.password = make_password(password)
        user.save()

        request.session["user-id"] = user.id

        return redirect("account:user-account")

    return render(request, 'account/register.html', {'random_number': random_number})

@required_login
def logout(request):
    request.session.flush()
    return redirect("account:login")

@required_login
def user_account(request):
    random_number = random.randint(1, 2000)
    return render(request, 'account/user-account.html', {'random_number': random_number})

@required_login
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