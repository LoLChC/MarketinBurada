from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    email_verify = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=128)
    birthday = models.DateField(null=True, blank=True)
    register_date = models.DateTimeField(auto_now_add=True)
    login_dates = models.JSONField(default=list, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def password_hash(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def password_check(self, raw_password):
        return check_password(raw_password, self.password)
    
    def delete_time(self):
        self.deleted_at = timezone.now()
        self.save()

    def delete_time_correct(self):
        if self.deleted_at:
            return timezone.now() >= self.deleted_at + timedelta(days=30)
        return False
