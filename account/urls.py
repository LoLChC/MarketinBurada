from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path("email-verification/", views.email_verification, name="email-verification"),
    path('verification-success/', views.verification_success, name="verification-success"),
    path('verification-unsuccess/', views.verification_unsuccess, name="verification-unsuccess"),
    path('logout/', views.logout, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    path('user-account/', views.user_account, name='user-account'),
    path('market-account/', views.market_account, name='market-account'),
    path('terms/', views.terms, name='terms'),
    path('kvkk/', views.kvkk, name='kvkk'),
]