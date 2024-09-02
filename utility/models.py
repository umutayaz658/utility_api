from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models
from .utils import AESUtil

aes_util = AESUtil()


class CustomURL(models.Model):
    short_url = models.CharField(max_length=255, unique=True)
    long_url = models.URLField(max_length=255)
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


class QuickNoteManager(models.Manager):
    def create_note(self, created_by, text, send_to=None):
        iv, encrypted_text = aes_util.encrypt(text)
        return self.create(
            created_at=timezone.now(),
            created_by=created_by,
            send_to=send_to,
            text=f"{iv}:{encrypted_text}"
        )

    def get_decrypted_text(self, note):
        iv, encrypted_text = note.text.split(':')
        return aes_util.decrypt(iv, encrypted_text)


class QuickNote(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    send_to = models.ForeignKey(User, related_name='received_notes', null=True, blank=True, on_delete=models.SET_NULL)
    text = models.TextField()

    objects = QuickNoteManager()
