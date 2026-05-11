from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    FollowUpTemplate, FollowUpRule, FollowUpSchedule, FollowUpHistory,
    FollowUpTrigger, FollowUpAnalytics, FollowUpBlacklist
)

User = get_user_model()


class FollowUpTemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = FollowUpTemplate
        fields = [
            'id', 'name', 'trigger_type', 'subject', 'content', 'variables',
            'delay_days', 'delay_hours', 'is_active', 'is_one_time', 'priority',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class FollowUpRuleSerializer(serializers.ModelSerializer):
    templates_info = FollowUpTemplateSerializer(source='templates', many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = FollowUpRule
        fields = [
            'id', 'name', 'description', 'condition_type', 'conditions',
            'templates', 'templates_info', 'is_active', 'start_date', 'end_date',
            'max_sends_per_candidate', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class FollowUpScheduleSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.get_full_name', read_only=True)
    candidate_email = serializers.EmailField(source='candidate.email', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    rule_name = serializers.CharField(source='rule.name', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model = FollowUpSchedule
        fields = [
            'id', 'candidate', 'candidate_name', 'candidate_email',
            'application', 'job', 'job_title', 'template', 'template_name',
            'rule', 'rule_name', 'scheduled_at', 'sent_at', 'status',
            'recipient_email', 'subject', 'content', 'variables_used',
            'attempts', 'max_attempts', 'last_error', 'opened_at',
            'clicked_at', 'replied_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'candidate', 'application', 'job', 'template', 'rule',
            'scheduled_at', 'sent_at', 'status', 'recipient_email',
            'subject', 'content', 'variables_used', 'attempts', 'last_error',
            'opened_at', 'clicked_at', 'replied_at', 'created_at', 'updated_at'
        ]


class FollowUpHistorySerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='schedule.template.name', read_only=True)
    candidate_email = serializers.EmailField(source='schedule.candidate.email', read_only=True)

    class Meta:
        model = FollowUpHistory
        fields = [
            'id', 'schedule', 'template_name', 'candidate_email',
            'action_type', 'action_date', 'details', 'notes'
        ]
        read_only_fields = ['id', 'schedule', 'action_date']


class FollowUpTriggerSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.get_full_name', read_only=True)
    candidate_email = serializers.EmailField(source='candidate.email', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model = FollowUpTrigger
        fields = [
            'id', 'event_type', 'application', 'candidate', 'candidate_name',
            'candidate_email', 'job', 'job_title', 'event_data', 'processed',
            'processed_at', 'schedules_created', 'errors', 'created_at'
        ]
        read_only_fields = [
            'id', 'application', 'candidate', 'job', 'event_data',
            'processed', 'processed_at', 'schedules_created', 'errors', 'created_at'
        ]


class FollowUpAnalyticsSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    rule_name = serializers.CharField(source='rule.name', read_only=True)

    class Meta:
        model = FollowUpAnalytics
        fields = [
            'id', 'date', 'template', 'template_name', 'rule', 'rule_name',
            'total_scheduled', 'total_sent', 'total_failed', 'total_opened',
            'total_clicked', 'total_replied', 'open_rate', 'click_rate',
            'reply_rate', 'success_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'date', 'template', 'rule', 'total_scheduled', 'total_sent',
            'total_failed', 'total_opened', 'total_clicked', 'total_replied',
            'open_rate', 'click_rate', 'reply_rate', 'success_rate',
            'created_at', 'updated_at'
        ]


class FollowUpBlacklistSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.get_full_name', read_only=True)
    candidate_email = serializers.EmailField(source='candidate.email', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = FollowUpBlacklist
        fields = [
            'id', 'candidate', 'candidate_name', 'candidate_email', 'job',
            'template', 'rule', 'reason', 'is_permanent', 'expires_at',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = [
            'id', 'candidate', 'job', 'template', 'rule',
            'created_by', 'created_at'
        ]


class FollowUpScheduleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUpSchedule
        fields = [
            'candidate', 'application', 'job', 'template', 'rule',
            'scheduled_at', 'recipient_email', 'subject', 'content', 'variables_used'
        ]


class FollowUpTriggerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUpTrigger
        fields = [
            'event_type', 'application', 'candidate', 'job', 'event_data'
        ]


class BulkFollowUpScheduleSerializer(serializers.Serializer):
    candidates = serializers.ListField(child=serializers.IntegerField())
    template_id = serializers.IntegerField()
    rule_id = serializers.IntegerField(required=False)
    scheduled_at = serializers.DateTimeField()
    subject_override = serializers.CharField(max_length=255, required=False)
    content_override = serializers.CharField(required=False)


class FollowUpTestSerializer(serializers.Serializer):
    template_id = serializers.IntegerField()
    candidate_id = serializers.IntegerField()
    variables = serializers.JSONField(default=dict)
    send_immediately = serializers.BooleanField(default=False)
