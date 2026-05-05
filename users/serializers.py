from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'password', 'role', 'plan']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = [
            'id', 'username', 'email', 'role', 'plan',
            'public_key', 'fcm_token',
            'two_factor_enabled',
            'failed_login_attempts', 'lockout_until',
        ]
        read_only_fields = [
            'two_factor_enabled',
            'failed_login_attempts',
            'lockout_until',
        ]