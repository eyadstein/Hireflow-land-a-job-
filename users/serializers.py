from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password',
            'role', 'plan', 'gender'
        ]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'email', 'role', 'plan', 'gender', 'phone',
            'location', 'bio', 'profile_photo',
            'skills', 'experience_level', 'desired_roles',
            'preferred_countries', 'prefers_remote',
            'years_of_experience', 'education',
            'linkedin_url', 'portfolio_url', 'resume_url',
            'is_profile_verified', 'badge', 'profile_completion',
            'public_key', 'fcm_token',
        ]
        read_only_fields = [
            'is_profile_verified', 'badge',
            'profile_completion', 'plan',
        ]