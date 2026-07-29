from django.http import JsonResponse
import merchant.models as  models
import core.utils as utils
import core.tokens as tokens

# Create your views here.

def stock_data(request):
    data = models.Stocks.get_all("1")
    response = JsonResponse({"Market" : data})
    return response 

def ailes(request):
    data = models.Aisles.get_all("1")
    response = JsonResponse({"Ailes" : data})
    return response

def products(request):
    data = models.Products.get_all("1")
    response = JsonResponse({"Products" : data})
    return response

def campaigns(request):
    data = models.Campaign.get_all("1")
    response = JsonResponse({"Campaign" : data})
    return response