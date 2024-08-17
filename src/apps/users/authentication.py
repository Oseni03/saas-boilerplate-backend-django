from channels.db import database_sync_to_async
from django.conf import settings
from django.http import parse_cookie
from rest_framework import HTTP_HEADER_ENCODING
from rest_framework_simplejwt import authentication



class CustomJWTAuthentication(authentication.JWTAuthentication):
    def authenticate(self, request):
        try:
            header = self.get_header(request)

            if header is None:
                raw_token = request.COOKIES.get(settings.AUTH_ACCESS_COOKIE)
            else:
                raw_token = self.get_raw_token(header)

            if raw_token is None:
                return None

            validated_token = self.get_validated_token(raw_token)

            return self.get_user(validated_token), validated_token
        except:
            return None


class JSONWebTokenChannelsAuthentication(authentication.JWTAuthentication):
    def get_header(self, scope):
        for name, value in scope.get("headers", []):
            if name == b"cookie":
                cookies = parse_cookie(value.decode("latin1"))
                break
        else:
            # No cookie header found - add an empty default.
            cookies = {}

        """
        Extracts the header containing the JSON web token from the given
        request.
        """
        header = cookies.get(settings.AUTH_ACCESS_COOKIE)

        if isinstance(header, str):
            # Work around django test client oddness
            header = header.encode(HTTP_HEADER_ENCODING)

        return header

    def get_raw_token(self, header):
        return header


class JSONWebTokenCookieMiddleware:
    def __init__(self, app):
        self.app = app

    @database_sync_to_async
    def authenticate(self, scope):
        auth_backend = JSONWebTokenChannelsAuthentication()
        return auth_backend.authenticate(scope)

    async def __call__(self, scope, receive, send):
        scope = dict(scope)
        result = await self.authenticate(scope)
        if result is not None:
            user, _ = result
            scope["user"] = user

        return await self.app(scope, receive, send)
