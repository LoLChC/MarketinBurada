from django.shortcuts import render
import random
from core.utils import home_market_cache

# Create your views here.

def home(request):
    random_number = random.randint(1, 2000)
    markets = home_market_cache()
    return render(request, 'main/home.html', {'random_number': random_number, 'markets' : markets})

def about(request):
    random_number = random.randint(1, 2000)
    return render(request, 'main/about.html', {'random_number': random_number})

def work_with_us(request):
    random_number = random.randint(1, 2000)
    return render(request, 'main/work-with-us.html', {'random_number': random_number})