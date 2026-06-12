from django.urls import path
from . import views

app_name = 'markets'

urlpatterns = [
    path('', views.markets, name='markets'),
    path('<slug:slug>/', views.market_details, name='market_detail'),
]