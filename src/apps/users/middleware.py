from django.core.exceptions import ImproperlyConfigured
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

from .models import UserProfile


def get_profile(request):
    if not hasattr(request, "_cached_user"):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        request._cached_profile = profile
    return request._cached_profile


class UserProfileMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, "user"):
            raise ImproperlyConfigured(
                "The Django remote user auth middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the UserProfileMiddleware class."
            )
        
        if request.user.is_authenticated:
            request.profile = SimpleLazyObject(lambda: get_profile(request))