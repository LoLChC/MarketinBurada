from django.shortcuts import render
import random
# Create your views here.

def home(request):
    random_number = random.randint(1, 2000)
    return render(request, 'main/home.html', {'random_number': random_number})

def about(request):
    random_number = random.randint(1, 2000)
    return render(request, 'main/about.html', {'random_number': random_number})

def login(request):
    random_number = random.randint(1, 2000)
    return render(request, 'main/login.html', {'random_number': random_number})

def register(request):
    random_number = random.randint(1, 2000)
    return render(request, 'main/register.html', {'random_number': random_number})