from django.conf import settings
import hashid_field
from django.db import models
from django.utils.text import slugify
import requests

# Create your models here.
class Thirdparty(models.Model):
    id: str = hashid_field.HashidAutoField(primary_key=True)
    name = models.CharField(max_length=150)
    auth_url = models.URLField()
    token_uri = models.URLField(null=True, blank=True)
    client_ID = models.CharField(max_length=250)
    client_secret = models.CharField(max_length=250)
    scopes = models.TextField(help_text="coma separated scopes")
    slug = models.SlugField(null=True, blank=True, unique=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through="Integrations")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return str(self.name)
    
    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(**args, **kwargs)
    
    @property
    def oauth_url(self) -> str:
        redirect_url = settings.INTEGRATION_REDIRECT_URL
        return f"{self.auth_url}?response_type=code&client_id={self.client_ID}&redirect_uri={redirect_url}&access_type=offline&prompt=consent&scope={self.scopes}"
    
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


class Integrations(models.Model):
    id: str = hashid_field.HashidAutoField(primary_key=True)
    thirdparty = models.ForeignKey(Thirdparty, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="integrations")
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    webhook_url = models.CharField(max_length=255, null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)