from rest_framework import serializers
from .models import Application, CandidateNote


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ['applicant', 'created_at']


class CandidateNoteSerializer(serializers.ModelSerializer):
    recruiter_name = serializers.CharField(source='recruiter.username', read_only=True)

    class Meta:
        model = CandidateNote
        fields = '__all__'
        read_only_fields = ['recruiter', 'created_at', 'updated_at']


class CandidateProfileSerializer(serializers.Serializer):
    """Read-only serializer for the full candidate profile."""
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    total_applications = serializers.IntegerField()
    pending = serializers.IntegerField()
    accepted = serializers.IntegerField()
    rejected = serializers.IntegerField()
    first_applied = serializers.DateTimeField(allow_null=True)
    last_applied = serializers.DateTimeField(allow_null=True)
    applications = ApplicationSerializer(many=True)
    notes_count = serializers.IntegerField()
