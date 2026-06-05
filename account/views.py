from django.shortcuts import render
import random
# Create your views here.

def login(request):
    random_number = random.randint(1, 2000)
    return render(request, 'account/login.html', {'random_number': random_number})

def register(request):
    random_number = random.randint(1, 2000)
    return render(request, 'account/register.html', {'random_number': random_number})

def forgot_password(request):
    random_number = random.randint(1, 2000)
    return render(request, 'account/forgot-password.html', {'random_number': random_number})

def terms(request):
    random_number = random.randint(1, 2000)
    return render(request, 'account/terms.html', {'random_number': random_number})

def kvkk(request):
    random_number = random.randint(1, 2000)
    return render(request, 'account/kvkk.html', {'random_number': random_number})
