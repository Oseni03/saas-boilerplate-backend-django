from django.dispatch import Signal
from django.db.models.signals import post_save
from .models import User

from apps.users import notifications, tokens


email_confirmed_signal = Signal()


def send_account_confirmation_email(sender, instance, *args, **kwargs):
    notifications.AccountActivationEmail(
        user=instance, data={'user_id': instance.id.hashid, 'token': tokens.account_activation_token.make_token(instance)}
    ).send()

post_save.connect(send_account_confirmation_email, sender=User)