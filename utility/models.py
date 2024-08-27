from django.contrib.auth.models import User
from django.db import models


class CustomURL(models.Model):
    short_url = models.CharField(max_length=255, unique=True)
    long_url = models.URLField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    validity_period = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    one_time_only = models.BooleanField(default=False)
    password = models.CharField(max_length=100, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
