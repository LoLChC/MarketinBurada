from . import views
from django.urls import path

urlpatterns = [
    path('stock-data/', views.stock_data, name='stock_data'),
    path('ailes/', views.ailes, name='ailes'),
    path('products/', views.products, name="products"),
    path('campaigns/', views.campaigns, name="campaigns"),
]