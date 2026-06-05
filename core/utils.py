from django.shortcuts import redirect

def login(request, user):
    request.session["user-id"] = user.id
    request.session["user-email"] = user.email
    
# Send Mail definition add here