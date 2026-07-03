import jwt
from django.contrib.auth import authenticate, get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import ActivityLog
from .permissions import IsAdmin
from .log import log_activity
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    ProfileSerializer,
    ChangePasswordSerializer,
    UserSerializer,
    ActivityLogSerializer,
)
from .auth import create_access_token, create_refresh_token, decode_token

User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    ser = RegisterSerializer(data=request.data)
    if not ser.is_valid():
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
    user = ser.save()
    log_activity(user, "register", request=request)
    return Response(
        {
            "access_token": create_access_token(user),
            "refresh_token": create_refresh_token(user),
            "user": ProfileSerializer(user).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    ser = LoginSerializer(data=request.data)
    if not ser.is_valid():
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
    user = authenticate(
        username=ser.validated_data["username"],
        password=ser.validated_data["password"],
    )
    if user is None:
        return Response(
            {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )
    if not user.is_active:
        return Response(
            {"detail": "Account disabled"}, status=status.HTTP_401_UNAUTHORIZED
        )
    log_activity(user, "login", request=request)
    return Response(
        {
            "access_token": create_access_token(user),
            "refresh_token": create_refresh_token(user),
            "user": ProfileSerializer(user).data,
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_view(request):
    token = request.data.get("refresh_token", "")
    if not token:
        return Response(
            {"detail": "refresh_token required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        return Response(
            {"detail": "Refresh token expired"},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    except jwt.InvalidTokenError:
        return Response(
            {"detail": "Invalid refresh token"},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    if payload.get("type") != "refresh":
        return Response(
            {"detail": "Invalid token type"}, status=status.HTTP_401_UNAUTHORIZED
        )
    user = User.objects.filter(id=payload["user_id"]).first()
    if user is None or not user.is_active:
        return Response(
            {"detail": "User not found"}, status=status.HTTP_401_UNAUTHORIZED
        )
    return Response({"access_token": create_access_token(user)})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    log_activity(request.user, "logout", request=request)
    return Response({"status": "ok"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    ser = ChangePasswordSerializer(data=request.data)
    if not ser.is_valid():
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
    if not request.user.check_password(ser.validated_data["old_password"]):
        return Response(
            {"detail": "Current password is incorrect"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    request.user.set_password(ser.validated_data["new_password"])
    request.user.save()
    log_activity(request.user, "change_password", request=request)
    return Response({"status": "ok"})


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def profile(request):
    if request.method == "GET":
        return Response(ProfileSerializer(request.user).data)
    ser = ProfileSerializer(request.user, data=request.data, partial=True)
    if not ser.is_valid():
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
    ser.save()
    log_activity(request.user, "update_profile", {"changes": list(ser.validated_data.keys())}, request)
    return Response(ser.data)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def user_list(request):
    if request.method == "POST":
        data = request.data.copy()
        password = data.pop("password", None)
        ser = UserSerializer(data=data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        user = ser.save()
        if password:
            user.set_password(password)
            user.save()
        log_activity(request.user, "create_user", {"user_id": user.id, "username": user.username}, request)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    users = User.objects.all().order_by("-date_joined")
    return Response(UserSerializer(users, many=True).data)


@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated, IsAdmin])
def user_detail(request, user_id):
    target = User.objects.filter(id=user_id).first()
    if target is None:
        return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if target.is_super_admin and not request.user.is_super_admin:
        return Response(
            {"detail": "Cannot modify a super admin"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == "DELETE":
        if target == request.user:
            return Response(
                {"detail": "Cannot delete yourself"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        target.is_active = False
        target.save()
        log_activity(request.user, "disable_user", {"user_id": target.id, "username": target.username}, request)
        return Response({"status": "ok"})

    ser = UserSerializer(target, data=request.data, partial=True)
    if not ser.is_valid():
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    if not request.user.is_super_admin:
        ser.validated_data.pop("email", None)
        ser.validated_data.pop("password", None)

    password = ser.validated_data.pop("password", None)
    ser.save()
    if password:
        target.set_password(password)
        target.save(update_fields=["password"])

    log_activity(request.user, "update_user", {"user_id": target.id, "changes": list(ser.validated_data.keys())}, request)
    return Response(UserSerializer(target).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def activity_log_view(request):
    logs = ActivityLog.objects.select_related("user").all()[:100]
    ser = ActivityLogSerializer(logs, many=True)
    return Response(ser.data)
