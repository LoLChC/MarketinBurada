from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    email_verify = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=128)
    birthday = models.DateField(null=True, blank=True)
    register_date = models.DateTimeField(auto_now_add=True)
    login_dates = models.JSONField(default=list, blank=True)

    def password_hash(self, raw_password):
        self.password = make_password(raw_password)

    def password_check(self, raw_password):
        return check_password(raw_password, self.password)
    

class Card(models.Model):   
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cards")

    card_holder = models.CharField(max_length=255)
    card_number = models.CharField(max_length=19)  # 16-19 hane (space dahil olabilir)
    expiry_month = models.PositiveSmallIntegerField()
    expiry_year = models.PositiveSmallIntegerField()
    card_cvv = models.CharField(max_length=4)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.card_holder} - {self.card_number[-4:]}"
    
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")

    title = models.CharField(max_length=100)          # Adres başlığı
    city = models.CharField(max_length=100)           # Şehir
    district = models.CharField(max_length=100)       # İlçe
    address_detail = models.TextField()               # Tam adres

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.card_holder} - {self.card_number[-4:]}"