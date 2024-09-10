import requests
import random
import string
from django.conf import settings
import hashid_field
from django.db import models
from django.utils.text import slugify


class Thirdparty(models.Model):
    id = hashid_field.HashidAutoField(primary_key=True)
    name = models.CharField(max_length=150)
    description = models.TextField()
    auth_url = models.URLField()
    token_uri = models.URLField(null=True, blank=True)
    revoke_uri = models.URLField(null=True, blank=True)
    client_ID = models.CharField(max_length=250)
    client_secret = models.CharField(max_length=250)
    state = models.CharField(max_length=250, null=True, blank=True)
    scopes = models.TextField(help_text="Comma-separated scopes")
    slug = models.SlugField(null=True, blank=True, unique=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through="Integration")
    is_active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Thirdparties"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.state:
            self.state = self.generate_state()
        super().save(*args, **kwargs)

    def generate_state(self, length=32):
        """Generate a cryptographically random state value."""
        return "".join(
            random.SystemRandom().choice(string.ascii_letters + string.digits)
            for _ in range(length)
        )

    @property
    def oauth_url(self) -> str:
        redirect_url = settings.INTEGRATION_REDIRECT_URL
        return f"{self.auth_url}?response_type=code&client_id={self.client_ID}&redirect_uri={redirect_url}&access_type=offline&prompt=consent&scope={self.scopes}&state={self.state}"

    def handle_oauth_callback(self, code):
        redirect_url = settings.INTEGRATION_REDIRECT_URL
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_url,
            "client_id": self.client_ID,
            "client_secret": self.client_secret,
        }
        response = requests.post(self.token_uri, data=data)
        return response.json()


class Integration(models.Model):
    id = hashid_field.HashidAutoField(primary_key=True)
    thirdparty = models.ForeignKey(Thirdparty, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="integrations"
    )
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    webhook_url = models.CharField(max_length=255, null=True, blank=True)
    id_token = models.TextField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def delete(self, *args, **kwargs):
        if self.access_token and not self.access_revoked:
            self.revoke_access_token()
        super().delete(*args, **kwargs)

    def revoke_access_token(self):
        revoke_url = self.thirdparty.revoke_uri or (
            self.thirdparty.token_uri.replace("token", "revoke")
            if self.thirdparty.token_uri
            else None
        )
        if not revoke_url:
            return False
        data = {
            "token": self.access_token,
            "client_id": self.thirdparty.client_ID,
            "client_secret": self.thirdparty.client_secret,
        }
        response = requests.post(revoke_url, data=data)
        return response.status_code == 200
