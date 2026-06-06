from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from . import tokens
from . import utils
from account.models import User

# Create your views here.

def read_verify_email(request):
    real_token = request.session.get("token")
    user_token = request.GET.get("token")
    user_id = request.session.get("user-id")

    if real_token == user_token:
        user = User.objects.filter(id=user_id).first()
        user.email_verify = True
        user.save()
        return redirect("account:verification-success")
    else:
        return redirect("account:verification-unsuccess")

def verify_email_looking(request):
    user_id = request.session.get("user-id")
    user = User.objects.filter(id=user_id).first()
    verify = user.email_verify
    if verify == True:
        ok = True
    else:
        ok = False

    return JsonResponse({"verify": ok})