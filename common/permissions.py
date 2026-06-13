from rest_framework.permissions import BasePermission
from apps.subscriptions.models import UserSubscription


class IsSubscribed(BasePermission):
    """
    Allow access only to users with an active subscription
    """
    
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        active_subscription = UserSubscription.objects.filter(
            customer=user,
            status="active"
        )
        return active_subscription.exists()