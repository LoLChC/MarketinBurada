from django.urls import path
from . import views

app_name = 'merchant'

urlpatterns = [
    path('a/', views.branchs, name='market_detail'),
    path('', views.dashboard)
]