from rest_framework import serializers
from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    display_title   = serializers.SerializerMethodField()
    display_company = serializers.SerializerMethodField()

    class Meta:
        model  = Application
        fields = [
            'id', 'user', 'job', 'company_name', 'job_title',
            'display_title', 'display_company', 'status', 'notes',
            'applied_date', 'order', 'quick_apply', 'ai_cover_letter',
            'ai_match_score', 'ai_matched_skills', 'ai_missing_skills',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'user', 'created_at', 'updated_at',
            'display_title', 'display_company',
            'quick_apply', 'ai_cover_letter', 'ai_match_score',
            'ai_matched_skills', 'ai_missing_skills',
        ]

    def get_display_title(self, obj):
        return obj.get_display_title()

    def get_display_company(self, obj):
        return obj.get_display_company()

    def validate(self, data):
        job          = data.get('job')
        company_name = data.get('company_name', '').strip()
        job_title    = data.get('job_title', '').strip()

        if not job and not (company_name and job_title):
            raise serializers.ValidationError(
                "Provide either a job ID or both company_name and job_title."
            )
        return data


class MoveCardSerializer(serializers.Serializer):
    STATUS_CHOICES = [s[0] for s in Application.KANBAN_STATUS_CHOICES]
    status = serializers.ChoiceField(choices=STATUS_CHOICES)
    order  = serializers.IntegerField(required=False, min_value=0)