from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('read-verify-email/', views.read_verify_email, name="read-verify-email"),
    path('verify-email-looking/', views.verify_email_looking, name="verify-email-looking"),
    path('read-forgot-password/', views.read_forgot_password, name="read-forgot-password"),
    path('clear-cache/', views.clear_cache, name="clear-cache"),
    path("address-delete/<int:pk>/", views.address_delete, name="address-delete"),
    path('try', views.trys, name="trys"),
]