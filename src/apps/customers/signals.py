from apps.users.signals import email_confirmed_signal
from django.contrib.auth import get_user_model

from .models import Customer

User = get_user_model()

def create_customer_callback(sender, instance, *args, **kwargs):
    Customer.objects.create(user=instance)

email_confirmed_signal.connect(create_customer_callback, User)