from django.shortcuts import render, get_object_or_404
import random
from markets.models import Market

# Create your views here.
def dashboard(request):
    random_number = random.randint(1, 2000)
    return render(request, 'merchant/merchant-account.html', {'random_number': random_number})

def branchs(request):
    random_number = random.randint(1, 2000)
    return render(request, 'merchant/branch-account.html', {'random_number': random_number})