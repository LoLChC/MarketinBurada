from django.shortcuts import render
import random

# Create your views here.

def markets(request):
    random_number = random.randint(1, 2000)
    return render(request, 'markets/markets.html', {'random_number': random_number})