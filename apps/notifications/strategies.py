import logging
from django.conf import settings

from common import emails
from . import email_serializers, models, utils

logger = logging.getLogger(__name__)

User = settings.AUTH_USER_MODEL


class NotificationEmail(emails.Email):
    def __init__(self, user, data=None):
        super().__init__(to=user.email, data=data)


class NotificationTypeEmail(NotificationEmail):
    """Email for specific notification type
    """
    
    name = 'Notification' # Notification Type name
    serializer_class = email_serializers.NotificationType # Serializer for the notification type


class BaseNotificationStrategy:
    @staticmethod
    def should_send_notification(user: User, type: str):
        """
        Based on strategy, user and notification type decide, if notification should be sent to user.
        Can be used if application allows user to disable specific notification channels or user can customize what
        notification types he wants to receive.
        """
        return True

    @staticmethod
    def send_notification(user: User, type: str, data: dict):
        raise NotImplementedError("Subclasses of BaseNotificationStrategy must provide a send_notification() function")


class InAppNotificationStrategy(BaseNotificationStrategy):
    @staticmethod
    def should_send_notification(user: User, type: str):
        return user.notification_preference.inapp_notification

    @staticmethod
    def send_notification(user: User, type: str, message: str, data: dict = None, issuer: str = None):
        models.Notification.objects.create(user=user, type=type, message=message, data=data, issuer=issuer)


class EmailNotificationStrategy(BaseNotificationStrategy):
    @staticmethod
    def should_send_notification(user: User, type: str):
        return user.notification_preference.email_notification

    @staticmethod
    def send_notification(user: User, type: str, message: str, data: dict = None, issuer: str = None):
        return NotificationTypeEmail(
            user=user, data={'user_id': user.id.hashid, "type": type, 'message': message}
        ).send()


class SMSNotificationStrategy(BaseNotificationStrategy):
    @staticmethod
    def should_send_notification(user: User, type: str):
        return user.notification_preference.sms_notification
    
    @staticmethod
    def send_notification(user: User, type: str, message: str, data: dict = None, issuer: str = None):
        return utils.send_sms_notification(user.profile.phone_number, message)


class PushNotificationStrategy(BaseNotificationStrategy):
    @staticmethod
    def should_send_notification(user: User, type: str):
        return user.notification_preference.push_notification
    
    @staticmethod
    def send_notification(user: User, type: str, message: str, data: dict = None, issuer: str = None):
        return utils.send_push_notification(user.profile.device_token, type, message)