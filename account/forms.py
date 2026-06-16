from django import forms
from .models import User
from django.core.exceptions import ValidationError

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
        

    