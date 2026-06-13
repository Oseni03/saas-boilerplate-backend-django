import hashid_field
from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('pending', 'Pending'),
    ]
    TYPE_CHOICES = [
        ('issue', 'Issue'),
        ('feedback', 'Feedback'),
    ]

    id: str = hashid_field.HashidAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name="tickets", null=True)
    full_name = models.CharField(max_length=250, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    assigned_to = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='feedback')
    rating = models.IntegerField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.status}"