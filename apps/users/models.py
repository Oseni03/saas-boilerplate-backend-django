from django.db import models
from django.contrib.auth.models import AbstractUser
import pyotp
import uuid

# Create your models here.
class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=32, blank=True, null=True)
    email_verification_token = models.CharField(max_length=32, blank=True, null=True)
    password_reset_token = models.CharField(max_length=32, blank=True, null=True)
    mfa_enabled = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
      app_label = "users"

    def __str__(self):
        return self.email

    def get_mfa_uri(self):
        if not self.mfa_secret:
            self.mfa_secret = pyotp.random_base32()
            self.save()
        return pyotp.totp.TOTP(self.mfa_secret).provisioning_uri(
            name=self.email, issuer_name="SaaS App"
        )