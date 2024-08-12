from rest_framework.permissions import BasePermission
from djstripe.models import Subscription


class IsSubscribed(BasePermission):
    """
    Allow access only to users with an active subscription
    """
    
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        
        user_profile = user.profile

        active_subscription = Subscription.objects.filter(
            customer=user_profile.customer,
            status="active"
        )
        return active_subscription.exists()