import hashid_field
from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
class Feedback(models.Model):
    id: str = hashid_field.HashidAutoField(primary_key=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='feedbacks')
    message = models.TextField()
    rating = models.IntegerField(null=True, blank=True)  # Optional rating (e.g., 1-5 stars)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.email} - {self.created_at}"