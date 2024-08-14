from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

from .models import Customer

User = get_user_model()

def create_customer_callback(sender, instance, *args, **kwargs):
    Customer.objects.create(user=instance)

post_save.connect(create_customer_callback, User)