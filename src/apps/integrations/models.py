from django.conf import settings
import hashid_field
from django.db import models
from django.utils.text import slugify
import requests

# Create your models here.
class Thirdparty(models.Model):
    id: str = hashid_field.HashidAutoField(primary_key=True)
    name = models.CharField(max_length=150)
    description = models.TextField()
    auth_url = models.URLField()
    token_uri = models.URLField(null=True, blank=True)
    revoke_uri = models.URLField(null=True, blank=True)
    client_ID = models.CharField(max_length=250)
    client_secret = models.CharField(max_length=250)
    scopes = models.TextField(help_text="coma separated scopes")
    slug = models.SlugField(null=True, blank=True, unique=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through="Integrations")
    is_active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Thirdparties"

    def __str__(self) -> str:
        return str(self.name)
    
    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(args, kwargs)
    
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

    access_revoked = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        models.UniqueConstraint(
            fields=["user", "thirdparty"], 
            name="unique_user_thirdparty",
        )
    
    def delete(self, *args, **kwargs):
        if self.access_token or not self.access_revoked:
            self.revoke_access_token()
        super().delete(*args, **kwargs)
    
    def revoke_access_token(self):
        # Assuming the third-party service supports token revocation at this endpoint
        if not self.thirdparty.revoke_uri and self.thirdparty.token_uri is not None:
            if self.thirdparty.token_uri.split("/")[-1] == "token":
                revoke_url = self.thirdparty.token_uri.replace("token", "revoke")
            else:
                revoke_url = self.thirdparty.token_uri + "/revoke"
        elif self.thirdparty.revoke_uri:
            revoke_url = self.thirdparty.revoke_uri
        else: 
            return False
        data = {
            "token": self.access_token,
            "client_id": self.thirdparty.client_ID,
            "client_secret": self.thirdparty.client_secret,
        }
        response = requests.post(revoke_url, data=data)
        if response.status_code == 200:
            return True
        else:
            # Handle error case if token revocation fails
            return False