from rest_framework import serializers
from .models import Job

class JobSerializer(serializers.ModelSerializer):
    posted_by_name = serializers.CharField(source='posted_by.username', read_only=True)

    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ['posted_by', 'created_at']