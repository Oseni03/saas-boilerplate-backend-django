from django.dispatch import Signal
from apps.subscriptions.models import UserSubscription
from apps.users import notifications, tokens
from common import billing

from .models import User

email_confirmed_signal = Signal()
send_account_confirmation_email_signal = Signal()
account_deactivated_signal = Signal()


def send_account_confirmation_email(sender, instance, *args, **kwargs):
    notifications.AccountActivationEmail(
        user=instance,
        data={
            "user_id": instance.id.hashid,
            "token": tokens.account_activation_token.make_token(instance),
        },
    ).send()


send_account_confirmation_email_signal.connect(
    send_account_confirmation_email, sender=User
)


def deactivate_user_account(sender, instance, *args, **kwargs):
    user = instance
    user.is_active = False
    user.save()

    user_subs = UserSubscription.objects.filter(user=user)
    if user_subs.exists() and user_subs.first().stripe_id:
        user_sub_obj = user_subs.first()
        response = billing.cancel_subscription(
            user_sub_obj.stripe_id,
            cancel_at_period_end=False,
            reason="User deactivate account",
        )
        for k, v in response.items():
            setattr(user_sub_obj, k, v)
        user_sub_obj.save()


account_deactivated_signal.connect(deactivate_user_account, sender=User)
