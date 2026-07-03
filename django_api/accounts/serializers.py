from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import ActivityLog

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
            role="officer",
            preferred_language="en",
        )


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    remember = serializers.BooleanField(default=False)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_super_admin",
            "preferred_language",
            "date_joined",
        )
        read_only_fields = ("id", "date_joined", "role", "is_super_admin")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=4)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_super_admin",
            "preferred_language",
            "is_active",
            "password",
            "date_joined",
        )
        read_only_fields = ("id", "date_joined", "is_super_admin", "username")

    def create(self, validated_data):
        validated_data.pop("is_super_admin", None)
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


class ActivityLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True, default="")

    class Meta:
        model = ActivityLog
        fields = ("id", "user", "username", "action", "details", "ip_address", "created_at")
        read_only_fields = ("id", "created_at")
