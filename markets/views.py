from django.shortcuts import render, get_object_or_404
import random
from .models import Market


def markets(request):
    random_number = random.randint(1, 2000)
    market = Market.objects.filter(status=True)
    return render(request, 'markets/markets.html', {'random_number': random_number , 'markets': market})

def market_details(request, slug):
    random_number = random.randint(1, 2000)
    market = get_object_or_404(Market, slug=slug)
    return render(request, 'markets/market-details.html', {'random_number': random_number , 'markets': market})