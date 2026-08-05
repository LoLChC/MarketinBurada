from django.shortcuts import render, redirect
import random
from .models import User, Card, Address
from django.contrib.auth.hashers import make_password
from core.decorators import required_login, required_logout
from core import utils
from core import tokens
from django.core.cache import cache
from core.redis_client import redis_conf as redis
from .forms import LoginForm, RegisterForm, ForgotPasswordForm, ForgotPasswordChangeForm, UserAccountForm, AddressAccountForm, CardAccountForm

# Create your views here.

@required_logout
def register(request):
    random_number = random.randint(1, 2000)

    if request.method == "POST":
        form = RegisterForm(request.POST)
        
        if form.is_valid():
            name = form.cleaned_data["name"]
            surname = form.cleaned_data["surname"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = User(name=name, surname=surname, email=email)
            user.password = make_password(password)
            user.save()

            return utils.login(request, user, "account:email-verification")

        error = None

        if "email" in form.errors:
            error = form.errors["email"][0]

        return render(request, "account/register.html", {"error": error, "random_number": random_number,})

    else:
        form = RegisterForm()

    
    return render(request, 'account/register.html', {'random_number': random_number})

@required_login
def email_verification(request):
    
    random_number = random.randint(1, 2000)

    user_id = utils.login_token_to_user_id(request)
    user = User.objects.filter(id=user_id).first()

    token = tokens.generate_email_verify_token(user)
    domain = request.get_host()    

    url = str("http://" + domain + "/core/read-verify-email?token=" + token)

    message = f"""
    <div style="font-family: Arial;">
        <h2>Email Doğrulama</h2>
        <p>Aşağıdaki butona tıkla:</p>

        <a href="{url}" 
        style="
                display:inline-block;
                padding:10px 15px;
                background:#4CAF50;
                color:white;
                text-decoration:none;
                border-radius:5px;"
            Doğrula
        </a>
    </div>
    """

    utils.send_mail_html("Trys",message, user.email)
    return render(request, 'account/email-verification.html', {'random_number': random_number})

def verification_success(request):
    random_number = random.randint(1, 2000)
    return render(request, 'account/verification-success.html', {'random_number': random_number})

def verification_unsuccess(request):
    random_number = random.randint(1, 2000)
    return render(request, 'account/verification-unsuccess.html', {'random_number': random_number})

@required_logout
def login(request):
    random_number = random.randint(1, 2000)
    
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].strip().lower()
            password = form.cleaned_data["password"]
            remember = form.cleaned_data["remember"]

            user = User.objects.filter(email=email).first()

            if not user:
                return render(request, 'account/login.html', {'error': 'Email veya şifre hatalı.','random_number': random_number})

            if not user.password_check(password):
                return render(request, 'account/login.html', {'error': 'Email veya şifre hatalı.','random_number': random_number})
            
            if remember:
                return utils.login(request, user, "account:user-account", 30)
            else:
                return utils.login(request, user, "account:user-account")
            
    else:
        form = LoginForm()
        
    return render(request, 'account/login.html', {'random_number': random_number})

@required_logout
def forgot_password(request):
    random_number = random.randint(1, 2000)
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]

            user = User.objects.filter(email=email).first()

            if user is None:
                return render(request, 'account/forgot-password.html', {'error': 'Bu email kayıtlı değil.', 'random_number': random_number})

            domain = request.get_host()
            code = tokens.generate_forgot_password_token(email)

            url = "http://" + domain + "/core/read-forgot-password?code=" + code 
            url = str(url)
            utils.send_mail_text("Şifre Sıfırlama", url, email)
            str_email = str(email)
            key = f"email:{str_email}"
            redis.set(
                key,
                str_email,
                ex=300,
            )
        
            return render(request, 'account/forgot-password.html', {'success': True, 'random_number': random_number})
        
        error = None

        if "email" in form.errors:
            error = form.errors["email"][0]

        return render(request, "account/forgot-password.html", {"error": error, "random_number": random_number,})
    
    else:
        form = ForgotPasswordForm()
        
    return render(request, 'account/forgot-password.html', {'random_number': random_number})

@required_logout
def forgot_password_change(request):
    if not request.COOKIES.get("password_reset_verified"):
        return redirect("account:forgot-password")
    
    random_number = random.randint(1, 2000)
    token_email = request.COOKIES.get("token_email")

    if request.method == "POST":
        form = ForgotPasswordChangeForm(request.POST)

        if form.is_valid():
            user = User.objects.filter(email=token_email).first()

            if user is not None:
                password = form.cleaned_data["password"]
                user.password = make_password(password)
                user.save()

                response = utils.login(request, user, "account:user-account")

                response.delete_cookie("password_reset_verified")
                response.delete_cookie("token_email")
                key = f"email:{token_email}"
                redis.delete(key)
            
                return response
            else:
                return redirect("account:forgot-password")

        error = None
        if form.non_field_errors():
            error = form.non_field_errors()[0]
        elif "password" in form.errors:
            error = form.errors["password"][0]
        elif "password_confirm" in form.errors:
            error = form.errors["password_confirm"][0]
        
        return render(request, 'account/forgot-password-change.html', {'error': error, 'random_number': random_number})
    
    else:
        form = ForgotPasswordChangeForm()
    
    return render(request, 'account/forgot-password-change.html', {'random_number': random_number})

@required_logout
def forgot_password_unchange(request):
    random_number = random.randint(1, 2000)
    request.session.flush()
    return render(request, 'account/forgot-password-unchange.html', {'random_number': random_number})

@required_login
def logout(request):
    return utils.logout(request)

@required_login
def user_account(request):
    random_number = random.randint(1, 2000)
    if request.user_obj.email_verify:
        user_obj = request.user_obj

        request.address = user_obj.addresses.all()
        request.card = user_obj.cards.all()

        address = request.address
        card = request.card

        if request.method == "POST":
            action = request.POST.get("action")

            user = User.objects.filter(id=user_obj.id).first()

            if not user:
                return redirect("account:login")

            # PROFILE UPDATE
            if action == "update_profile":
                UserForm = UserAccountForm(request.POST)
                if UserForm.is_valid():

                    phone = UserForm.cleaned_data.get('phone_number')
                    birth = UserForm.cleaned_data.get('birthday')

                    user.phone_number = phone
                    user.birthday = birth
                    user.save()

                    cache.set(f"user-{user.id}", user, timeout=300)
                    request.user_obj = user

                    return redirect("account:user-account")

            # DELETE ACCOUNT (SOFT DELETE)
            if action == "delete_account":
                user.delete()

                response = utils.logout(request)
                keys = [
                    f"email:{str(user.id)}",
                    f"email_verify:{str(user.id)}"
                ]
                
                if keys:
                    redis.delete(*keys)

                request.session.flush()
                cache.clear()

                for cookie_name in request.COOKIES.keys():
                        response.delete_cookie(
                            key=cookie_name,
                            path='/',
                            domain=None
                        )

                return response
            
            if action == "add_address":
                AddressForm = AddressAccountForm(request.POST)
                if AddressForm.is_valid():
                    address_title = AddressForm.cleaned_data.get('address_title')
                    city = AddressForm.cleaned_data.get('city')
                    district = AddressForm.cleaned_data.get('district')
                    address_detail = AddressForm.cleaned_data.get('address_detail')

                    Address.objects.create(user=user, title=address_title, city=city, district=district, address_detail=address_detail)

                    return redirect("account:user-account")

            if action == "add_card":
                CardForm = CardAccountForm(request.POST)
                if CardForm.is_valid():
                    card_holder = CardForm.cleaned_data.get('card_holder')
                    card_number = CardForm.cleaned_data.get('card_number')
                    expiry_month = CardForm.cleaned_data.get('expiry_month')
                    expiry_year = CardForm.cleaned_data.get('expiry_year')
                    card_cvv = CardForm.cleaned_data.get('card_cvv')
                    card_type = CardForm.cleaned_data.get('card_type')

                    Card.objects.create(user=user, card_holder=card_holder, card_number=card_number, expiry_month=expiry_month, expiry_year=expiry_year, card_cvv=card_cvv, card_type=card_type)
                    
                    return redirect("account:user-account")

        if not address.exists():
            return render(
                    request,
                    'account/user-account.html',
                    {
                        'random_number': random_number,
                        'card' : card, 
                        'address' : address,
                        'no_address' : True,
                    }
                    )
        return render(
                    request,
                    'account/user-account.html',
                    {
                        'random_number': random_number,
                        'card' : card, 
                        'address' : address,
                    }
                    )

    return redirect("account:email-verification")

def cart(request):
    random_number = random.randint(1, 2000)
    return render(request, 'account/cart.html', {'random_number': random_number})

@required_login
def market_account(request):
    random_number = random.randint(1, 2000)
    return render(request, 'account/market-account.html', {'random_number': random_number})

def terms(request):
    random_number = random.randint(1, 2000)
    return render(request, 'account/terms.html', {'random_number': random_number})

def kvkk(request):
    random_number = random.randint(1, 2000)
    return render(request, 'account/kvkk.html', {'random_number': random_number})