import datetime
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()

ACCESS_TOKEN_TTL = datetime.timedelta(hours=24)
REFRESH_TOKEN_TTL = datetime.timedelta(days=7)


def create_access_token(user) -> str:
    now = datetime.datetime.now(datetime.UTC)
    return jwt.encode(
        {
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
            "is_super_admin": user.is_super_admin,
            "type": "access",
            "iat": now,
            "exp": now + ACCESS_TOKEN_TTL,
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )


def create_refresh_token(user) -> str:
    now = datetime.datetime.now(datetime.UTC)
    return jwt.encode(
        {
            "user_id": user.id,
            "type": "refresh",
            "iat": now,
            "exp": now + REFRESH_TOKEN_TTL,
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        header = request.META.get("HTTP_AUTHORIZATION", "")
        if not header.startswith("Bearer "):
            return None
        token = header.removeprefix("Bearer ")
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")
        if payload.get("type") != "access":
            raise AuthenticationFailed("Invalid token type")
        user = User.objects.filter(id=payload.get("user_id")).first()
        if user is None:
            raise AuthenticationFailed("User not found")
        if not user.is_active:
            raise AuthenticationFailed("User is disabled")
        return (user, None)
