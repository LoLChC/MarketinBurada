from django.shortcuts import render
import random

# Create your views here.
def home(request):
    random_number = random.randint(1, 2000)
    return render(request, 'merchant/merchant-account.html', {'random_number': random_number})