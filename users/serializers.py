import re

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()

STRICT_EMAIL_REGEX = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        validators=[validate_password],
        error_messages={
            "required": "Password is required.",
            "blank": "Password is required.",
            "min_length": "Password must be at least 6 characters.",
        },
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "role",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "username": {"required": False, "allow_blank": True},
            "email": {
                "required": True,
                "error_messages": {
                    "required": "Email is required.",
                    "blank": "Email is required.",
                    "invalid": "Enter a valid email address.",
                },
            },
            "role": {"required": False},
        }

    def validate_email(self, value):
        value = value.strip().lower()

        if not STRICT_EMAIL_REGEX.match(value):
            raise serializers.ValidationError(
                "Enter a valid email address, for example name@example.com."
            )

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        return value

    def validate_username(self, value):
        if not value:
            return value

        value = value.strip()

        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already taken.")

        return value

    def validate_role(self, value):
        if not value:
            return "jobseeker"

        allowed_roles = [choice[0] for choice in User.ROLE_CHOICES]

        if value not in allowed_roles:
            raise serializers.ValidationError("Invalid role.")

        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        email = validated_data.get("email", "").strip().lower()
        username = validated_data.get("username", "").strip()
        role = validated_data.get("role", "jobseeker")

        if not username:
            username = email

        user = User(
            username=username,
            email=email,
            role=role,
        )

        user.set_password(password)
        user.save()

        return user


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "plan",
            "bio",
            "skills",
            "experience_level",
            "desired_roles",
            "preferred_countries",
            "prefers_remote",
            "city",
            "country",
            "linkedin",
            "portfolio",
            "public_key",
            "fcm_token",
        ]

        read_only_fields = [
            "id",
            "username",
            "email",
            "role",
            "plan",
        ]

    def get_full_name(self, obj):
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name or obj.username or obj.email

    def validate_linkedin(self, value):
        return value.strip() if value else ""

    def validate_portfolio(self, value):
        return value.strip() if value else ""

    def update(self, instance, validated_data):
        allowed_fields = [
            "first_name",
            "last_name",
            "bio",
            "skills",
            "experience_level",
            "desired_roles",
            "preferred_countries",
            "prefers_remote",
            "city",
            "country",
            "linkedin",
            "portfolio",
            "public_key",
            "fcm_token",
        ]

        for field in allowed_fields:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        instance.save()
        return instance