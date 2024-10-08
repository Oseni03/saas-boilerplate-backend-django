from functools import lru_cache

from django.conf import settings

from . import strategies
from .exceptions import NotificationStrategyException

User = settings.AUTH_USER_MODEL

@lru_cache
def get_enabled_strategies():
    enabled_strategies = []
    for enabled_strategy in settings.NOTIFICATIONS_STRATEGIES:
        try:
            strategy = getattr(strategies, enabled_strategy)
        except AttributeError:
            raise NotificationStrategyException(f"Notifications strategy '{enabled_strategy}' not found.")
        if not issubclass(strategy, strategies.BaseNotificationStrategy):
            raise NotificationStrategyException(
                f"Notification strategy '{enabled_strategy}' is not subclass of BaseNotificationStrategy."
            )
        enabled_strategies.append(strategy)
    return enabled_strategies


def send_notification(user: User, type: str, message: str, data: dict = None, issuer: str = None):
    for strategy in get_enabled_strategies():
        if strategy.should_send_notification(user, type):
            strategy.send_notification(user, type, message, data, issuer)
