from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'role']

    def create(self, validated_data):
        email = validated_data['email']
        validated_data['username'] = email
        user = User.objects.create_user(**validated_data)
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'plan',
            'bio', 'skills', 'experience_level', 'desired_roles',
            'preferred_countries', 'prefers_remote',
            'city', 'country', 'linkedin', 'portfolio',
        ]
        read_only_fields = ['id', 'username', 'email', 'role', 'plan']