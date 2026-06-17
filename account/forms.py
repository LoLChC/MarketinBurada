from django import forms
from .models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone

class RegisterForm(forms.Form):
    name = forms.CharField(max_length=50)
    surname = forms.CharField(max_length=50)
    email = forms.EmailField()
    password = forms.CharField(max_length=128)

    def clean_email(self):
        email = self.cleaned_data["email"]
        email = email.strip().lower()

        if User.objects.filter(email=email).exists():
            raise ValidationError("Bu email zaten kayıtlı")

        return email

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu email kayıtlı değil.")

        return email

class ForgotPasswordChangeForm(forms.Form):
    password = forms.CharField(min_length=6)
    password_confirm = forms.CharField()

    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], dict):
            data = args[0].copy()
            if 'password-confirm' in data:
                data['password_confirm'] = data.get('password-confirm')
            args = (data,) + args[1:]
            
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Girdiğiniz şifreler birbiriyle eşleşmiyor.")
            
        return cleaned_data

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(max_length=128)
    remember = forms.BooleanField(required=False)

    def clean_email(self):
        email = self.cleaned_data["email"]
        return email.strip().lower()
    
class UserAccountForm(forms.Form):
    phone_number = forms.CharField(max_length=20, required=False, validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Geçersiz telefon numarası.")])
    birthday = forms.DateField(required=False)

    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], dict):
            data = args[0].copy()
            if 'phone-number' in data:
                data['phone_number'] = data.get('phone-number')
            args = (data,) + args[1:]
            
        super().__init__(*args, **kwargs)

class AddressAccountForm(forms.Form):
    address_title = forms.CharField(max_length=100, required=True)
    city = forms.CharField(max_length=100, required=True)
    district = forms.CharField(max_length=100, required=True)
    address_detail = forms.CharField(required=True, widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], dict):
            data = args[0].copy()
            if 'address-title' in data:
                data['address_title'] = data.get('address-title')
            if 'address-detail' in data:
                data['address_detail'] = data.get('address-detail')
            args = (data,) + args[1:]
            
        super().__init__(*args, **kwargs)

class CardAccountForm(forms.Form):
    card_holder = forms.CharField(max_length=255, required=True)
    card_number = forms.CharField(max_length=19, required=True)
    card_expiry = forms.CharField(max_length=5, required=True)
    card_cvv = forms.CharField(max_length=4, required=True)

    expiry_month = forms.IntegerField(required=False, widget=forms.HiddenInput())
    expiry_year = forms.IntegerField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], dict):
            data = args[0].copy()
            if 'card-holder' in data:
                data['card_holder'] = data.get('card-holder')
            if 'card-number' in data:
                data['card_number'] = data.get('card-number')
            if 'card-expiry' in data:
                data['card_expiry'] = data.get('card-expiry')
            if 'card-cvv' in data:
                data['card_cvv'] = data.get('card-cvv')
            args = (data,) + args[1:]
            
        super().__init__(*args, **kwargs)

    def clean_card_number(self):
        card_number = self.cleaned_data.get('card_number', '').replace(" ", "").replace("-", "")
        
        if not card_number.isdigit():
            raise ValidationError("Kart numarası sadece rakamlardan oluşmalıdır.")
            
        card_type = "Unknown"
        if card_number.startswith('4'):
            card_type = "Visa"
        elif card_number.startswith(('51', '52', '53', '54', '55')) or (2221 <= int(card_number[:4]) <= 2720):
            card_type = "Mastercard"
        elif card_number.startswith(('34', '37')):
            card_type = "American Express (Amex)"
        elif card_number.startswith('9792'):
            card_type = "Troy"
        elif card_number.startswith(('6011', '65')) or (644 <= int(card_number[:3]) <= 649):
            card_type = "Discover"
            
        if card_type == "Unknown":
            raise ValidationError("Desteklenmeyen veya geçersiz bir kart tipi.")

        if card_type == "American Express (Amex)" and len(card_number) != 15:
            raise ValidationError("Amex kartlar 15 haneli olmalıdır.")
        elif card_type != "American Express (Amex)" and len(card_number) != 16:
            raise ValidationError(f"{card_type} kartlar 16 haneli olmalıdır.")

        digits = [int(d) for d in card_number[::-1]]
        
        for i in range(1, len(digits), 2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
                
        if sum(digits) % 10 != 0:
            raise ValidationError("Geçersiz kredi kartı numarası (Luhn kontrolü başarısız).")

        # clean_card_number içinde self.cleaned_data['card_type'] ataması yapıyoruz
        self.cleaned_data['card_type'] = card_type
        
        return card_number

    def clean_card_cvv(self):
        cvv = self.cleaned_data.get('card_cvv')
        if not cvv.isdigit():
            raise ValidationError("CVV sadece rakamlardan oluşmalıdır.")
        if len(cvv) < 3 or len(cvv) > 4:
            raise ValidationError("CVV 3 veya 4 haneli olmalıdır.")
        return cvv

    def clean(self):
        cleaned_data = super().clean()
        card_expiry = cleaned_data.get('card_expiry', '')

        if card_expiry and '/' in card_expiry:
            try:
                month_str, year_str = card_expiry.split('/')
                month = int(month_str)
                year = int(year_str)

                if year < 100:
                    year += 2000

                if month < 1 or month > 12:
                    raise ValidationError("Ay 1 ile 12 arasında olmalıdır.")

                current_year = timezone.now().year
                current_month = timezone.now().month

                if year < current_year or (year == current_year and month < current_month):
                    raise ValidationError("Kartın son kullanma tarihi geçmiş.")

                cleaned_data['expiry_month'] = month
                cleaned_data['expiry_year'] = year
            except ValueError:
                raise ValidationError("Geçersiz son kullanma tarihi formatı (AA/YY).")
        else:
            if 'card_expiry' in cleaned_data: # Hata zaten üst katmanda yoksa ekle
                raise ValidationError("Son kullanma tarihi AA/YY formatında olmalıdır.")

        return cleaned_data