from rest_framework import serializers
from .models import Job, SavedJob
from .models import Job, SavedJob, JobAlert, AlertMatch


class JobSerializer(serializers.ModelSerializer):
    posted_by_name = serializers.CharField(
        source='posted_by.username',
        read_only=True
    )

    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ['posted_by', 'created_at']


class SavedJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedJob
        fields = '__all__'
        read_only_fields = ['user', 'saved_at']


class JobAlertSerializer(serializers.ModelSerializer):
    matches_count = serializers.SerializerMethodField()
    unseen_count = serializers.SerializerMethodField()

    class Meta:
        model = JobAlert
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'last_triggered']

    def get_matches_count(self, obj):
        return obj.matches.count()

    def get_unseen_count(self, obj):
        return obj.matches.filter(is_seen=False).count()


class AlertMatchSerializer(serializers.ModelSerializer):
    alert_keywords = serializers.CharField(
        source='alert.keywords',
        read_only=True
    )

    class Meta:
        model = AlertMatch
        fields = '__all__'