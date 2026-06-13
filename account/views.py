from django.shortcuts import render, redirect
import random
from .models import User, Card, Address
from django.contrib.auth.hashers import make_password
from core.decorators import required_login, required_logout
from django.db.models import Q
from core import utils
from core import tokens
from django.core.cache import cache

# Create your views here.

@required_logout
def register(request):
    random_number = random.randint(1, 2000)

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email").lower().strip()
        password = request.POST.get("password")

        if User.objects.filter(email=email).exists():
            return render(request, 'account/register.html', {'error': 'Bu email zaten kayıtlı.', 'random_number': random_number})
        if User.objects.filter(name=name).exists():
            return render(request, 'account/register.html', {'error': 'Bu kullanıcı adı zaten kayıtlı.', 'random_number': random_number})

        user = User(name=name, email=email)
        user.password = make_password(password)
        user.save()

        request.session["user-id"] = user.id

        return redirect("account:email-verification")
    
    return render(request, 'account/register.html', {'random_number': random_number})

def email_verification(request):
    random_number = random.randint(1, 2000)
    domain = request.get_host() 
    token = tokens.generate_slug()

    request.session["token"] = token

    url = "http://" + domain + "/core/read-verify-email?token=" + token
    url = str(url)

    user_id = request.session.get("user-id")

    user = User.objects.filter(id=user_id).only("email").first()
    email = user.email

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
                border-radius:5px;">
            Doğrula
        </a>
    </div>
    """

    utils.send_mail_html("Trys",message, email)
    return render(request, 'account/email-verification.html', {'random_number': random_number})

def verification_success(request):
    del request.session['token']
    random_number = random.randint(1, 2000)
    return render(request, 'account/verification-success.html', {'random_number': random_number})

def verification_unsuccess(request):
    random_number = random.randint(1, 2000)
    return render(request, 'account/verification-unsuccess.html', {'random_number': random_number})

@required_logout
def login(request):
    random_number = random.randint(1, 2000)
    
    if request.method == "POST":
        username_or_email = request.POST.get("username-or-email")
        password = request.POST.get("password")
        remember = request.POST.get("remember")

        value = username_or_email.strip()
        user = User.objects.filter(Q(email=value.lower()) | Q(name=value)).first()

        if not user:
            return render(request, 'account/login.html', {'error': 'Kullanıcı adı veya email hatalı.','random_number': random_number})

        if not user.password_check(password):
            return render(request, 'account/login.html', {'error': 'Hatalı şifre.','random_number': random_number})
        
        request.session["user-id"] = user.id
        
        if not remember:
            request.session.set_expiry(0)
            
        return redirect("account:user-account")

    return render(request, 'account/login.html', {'random_number': random_number})

@required_logout
def forgot_password(request):
    random_number = random.randint(1, 2000)
    if request.method == "POST":
        email = request.POST.get("email")
        email = email.strip().lower()
        user = User.objects.filter(email=email).first()

        if user is None:
            return render(request, 'account/forgot-password.html', {'error': 'Bu email kayıtlı değil.', 'random_number': random_number})

        domain = request.get_host() 
        code = tokens.generate_forgot_password_token()
        request.session["code"] = code
        request.session["user-code-email"] = email

        url = "http://" + domain + "/core/read-forgot-password?code=" + code 
        url = str(url)
        utils.send_mail_text("Şifre Sıfırlama", url, email)
        
        return render(request, 'account/forgot-password.html', {'success': True, 'random_number': random_number})

    return render(request, 'account/forgot-password.html', {'random_number': random_number})

@required_logout
def forgot_password_change(request):
    if request.session.get("password-reset-verified"):
        random_number = random.randint(1, 2000)
        if request.method == "POST":
            password = request.POST.get("password")
            user_code_email = request.session.get("user-code-email")
            user = User.objects.filter(email=user_code_email).first()
            if user is not None:
                print("user var")
                user.password = make_password(password)
                user.save()
                print("user kaydedildi")
            else:
                return redirect("account:forgot-password")
            request.session["user-id"] = user.id
            print("login alındı")
            print("user_code_email:", user_code_email)
            print("bulunan user id:", user.id)
            print(request.session.get("user-id"))
            del request.session["user-code-email"]
            del request.session["password-reset-verified"]
            return redirect("account:user-account")

        return render(request, 'account/forgot-password-change.html', {'random_number': random_number})
    return redirect("account:forgot-password")

@required_logout
def forgot_password_unchange(request):
    random_number = random.randint(1, 2000)
    request.session.flush()
    return render(request, 'account/forgot-password-unchange.html', {'random_number': random_number})

@required_login
def logout(request):
    request.session.flush()
    return redirect("account:login")

@required_login
def user_account(request):
    random_number = random.randint(1, 2000)
    user_obj = request.user_obj

    if request.method == "POST":
        action = request.POST.get("action")

        user = User.objects.filter(id=user_obj.id).first()

        if not user:
            return redirect("account:login")

        # PROFILE UPDATE
        if action == "update_profile":
            birthday = request.POST.get("birthday")
            phone_number = request.POST.get("phone_number")

            user.phone_number = phone_number
            user.birthday = birthday
            user.save()

            cache.set(f"user-{user.id}", user, timeout=300)
            request.user_obj = user

            return redirect("account:user-account")

        # DELETE ACCOUNT (SOFT DELETE)
        if action == "delete_account":
            user.delete_time()  # deleted_at set ediyor

            # cache temizle
            cache.delete(f"user-{user.id}")

            # session kapat
            request.session.flush()

            return redirect("account:login")
        
        if action == "add_address":
            address_title = request.POST.get("address-title")
            city = request.POST.get("city")
            district = request.POST.get("district")
            address_detail = request.POST.get("address-detail")

            Address.objects.create(user=user, title=address_title, city=city, district=district, address_detail=address_detail)

        if action == "add_card":
            card_holder = request.POST.get("card-holder")
            card_number = request.POST.get("card-number")
            card_expiry = request.POST.get("card-expiry")  # "AA/YY"
            card_cvv = request.POST.get("card-cvv")

            if not (card_holder and card_number and card_expiry and card_cvv):
                return redirect("account:user-account")

            try:
                expiry_month, expiry_year = card_expiry.split("/")
                expiry_month = int(expiry_month)
                expiry_year = int("20" + expiry_year)  # 29 -> 2029 gibi

            except:
                return redirect("account:user-account")

            # kart numarasını temizle (boşlukları kaldır)
            card_number = card_number.replace(" ", "")

            Card.objects.create(user=user, card_holder=card_holder, card_number=card_number, expiry_month=expiry_month, expiry_year=expiry_year, card_cvv=card_cvv)

            return redirect("account:user-account")


    return render(request, 'account/user-account.html', {'random_number': random_number})

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