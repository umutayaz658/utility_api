from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.contrib.auth.models import User, PermissionsMixin, AbstractBaseUser
from django.db import models


class CustomURL(models.Model):
    short_url = models.CharField(max_length=255, unique=True)
    long_url = models.URLField(max_length=2048)
    created_at = models.DateTimeField(default=timezone.now)
    validity_period = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    one_time_only = models.BooleanField(default=False)
    password = models.CharField(max_length=100, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            print(self.password)
            self.password = make_password(self.password)
            print(self.password)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.validity_period


class QuickNote(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    send_to = models.ForeignKey(User, related_name='received_notes', null=True, blank=True, on_delete=models.SET_NULL)
    text = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='uploads/', null=True, blank=True)


class QRCode(models.Model):
    data = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='qr_codes/')
    created_at = models.DateTimeField(auto_now_add=True)


class PDF(models.Model):
    pdf = models.FileField(upload_to='pdfs/')
    created_at = models.DateTimeField(auto_now_add=True)
