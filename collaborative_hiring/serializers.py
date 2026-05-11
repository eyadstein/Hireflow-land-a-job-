from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    HiringTeam, HiringDecision, InterviewSchedule, CandidateFeedback,
    HiringWorkflow, JobWorkflow, TeamCollaboration, InterviewKit,
    JobInterviewKit, HiringAnalytics, TeamNotification
)

User = get_user_model()


class HiringTeamSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = HiringTeam
        fields = [
            'id', 'name', 'description', 'team_type', 'job', 'is_active',
            'created_by', 'created_by_name', 'member_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by_name', 'member_count']
    
    def get_member_count(self, obj):
        return obj.members.count()


class HiringDecisionSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.get_full_name', read_only=True)
    
    class Meta:
        model = HiringDecision
        fields = [
            'id', 'application', 'reviewer', 'reviewer_name', 'decision', 'score',
            'comments', 'strengths', 'concerns', 'recommendation', 'is_final',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['reviewer_name']


class InterviewScheduleSerializer(serializers.ModelSerializer):
    interviewers = serializers.StringRelatedField(many=True, read_only=True)
    candidate_name = serializers.CharField(source='candidate.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = InterviewSchedule
        fields = [
            'id', 'application', 'interview_type', 'title', 'description',
            'scheduled_date', 'duration_minutes', 'location', 'meeting_url',
            'interviewers', 'candidate', 'candidate_name', 'status',
            'feedback', 'rating', 'would_hire', 'internal_notes',
            'candidate_notes', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['interviewers', 'candidate_name', 'created_by_name']


class CandidateFeedbackSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.get_full_name', read_only=True)
    
    class Meta:
        model = CandidateFeedback
        fields = [
            'id', 'application', 'reviewer', 'reviewer_name', 'feedback_type',
            'score', 'max_score', 'strengths', 'weaknesses', 'observations',
            'recommendations', 'hire_recommendation', 'is_shared_with_candidate',
            'is_shared_with_team', 'created_at', 'updated_at'
        ]
        read_only_fields = ['reviewer_name']


class HiringWorkflowSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = HiringWorkflow
        fields = [
            'id', 'name', 'description', 'workflow_type', 'stages',
            'is_default', 'is_active', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by_name']


class JobWorkflowSerializer(serializers.ModelSerializer):
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    current_stage = serializers.CharField(read_only=True)
    
    class Meta:
        model = JobWorkflow
        fields = [
            'id', 'job', 'workflow', 'workflow_name', 'current_stage',
            'stage_history', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['workflow_name']


class TeamCollaborationSerializer(serializers.ModelSerializer):
    initiator_name = serializers.CharField(source='initiator.get_full_name', read_only=True)
    participant_names = serializers.SerializerMethodField()
    
    class Meta:
        model = TeamCollaboration
        fields = [
            'id', 'application', 'collaboration_type', 'title', 'message',
            'attachments', 'initiator', 'initiator_name', 'participants',
            'participant_names', 'status', 'priority', 'resolution',
            'resolved_by', 'resolved_by_name', 'resolved_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['initiator_name', 'participant_names', 'resolved_by_name']
    
    def get_participant_names(self, obj):
        return [user.get_full_name() for user in obj.participants.all()]


class InterviewKitSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    usage_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = InterviewKit
        fields = [
            'id', 'name', 'description', 'job_category', 'questions',
            'evaluation_criteria', 'scoring_rubric', 'time_allocations',
            'resources', 'templates', 'is_public', 'usage_count',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by_name', 'usage_count']


class JobInterviewKitSerializer(serializers.ModelSerializer):
    kit_name = serializers.CharField(source='interview_kit.name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    assigned_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = JobInterviewKit
        fields = [
            'id', 'job', 'interview_kit', 'kit_name', 'is_active',
            'assigned_by', 'assigned_by_name', 'assigned_at'
        ]
        read_only_fields = ['kit_name', 'assigned_by_name']


class HiringAnalyticsSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    
    class Meta:
        model = HiringAnalytics
        fields = [
            'id', 'metric_type', 'date', 'value', 'metadata',
            'job', 'team', 'workflow', 'job_title', 'team_name', 'workflow_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['job_title', 'team_name', 'workflow_name']


class TeamNotificationSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.name', read_only=True)
    is_sent = serializers.BooleanField(read_only=True)
    is_read = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = TeamNotification
        fields = [
            'id', 'team', 'team_name', 'notification_type', 'title', 'message',
            'related_object_id', 'related_object_type', 'is_sent', 'sent_at',
            'delivery_method', 'is_read', 'read_at', 'created_at'
        ]
        read_only_fields = ['team_name', 'is_sent', 'is_read', 'read_at']


# Create serializers
class HiringTeamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HiringTeam
        fields = ['name', 'description', 'team_type', 'job', 'members', 'is_active']


class HiringDecisionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HiringDecision
        fields = ['application', 'decision', 'score', 'comments', 'strengths', 'concerns', 'recommendation']


class InterviewScheduleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewSchedule
        fields = [
            'application', 'interview_type', 'title', 'description',
            'scheduled_date', 'duration_minutes', 'location', 'meeting_url',
            'interviewers', 'candidate'
        ]


class CandidateFeedbackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateFeedback
        fields = [
            'application', 'feedback_type', 'score', 'max_score',
            'strengths', 'weaknesses', 'observations', 'recommendations',
            'is_shared_with_candidate', 'is_shared_with_team'
        ]


class HiringWorkflowCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HiringWorkflow
        fields = ['name', 'description', 'workflow_type', 'stages', 'is_default', 'is_active']


class JobWorkflowCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobWorkflow
        fields = ['job', 'workflow', 'current_stage']


class TeamCollaborationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamCollaboration
        fields = [
            'application', 'collaboration_type', 'title', 'message',
            'participants', 'priority'
        ]


class InterviewKitCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewKit
        fields = ['name', 'description', 'job_category', 'questions', 'evaluation_criteria']


class JobInterviewKitCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobInterviewKit
        fields = ['job', 'interview_kit', 'is_active']


class HiringAnalyticsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HiringAnalytics
        fields = ['metric_type', 'date', 'value', 'metadata', 'job', 'team', 'workflow']


class TeamNotificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamNotification
        fields = ['team', 'notification_type', 'title', 'message', 'delivery_method']


# Bulk operations serializers
class BulkInterviewScheduleSerializer(serializers.Serializer):
    interviews = InterviewScheduleCreateSerializer(many=True)
    
    class Meta:
        fields = ['interviews']


class BulkFeedbackRequestSerializer(serializers.Serializer):
    application_id = serializers.IntegerField()
    feedback_requests = CandidateFeedbackCreateSerializer(many=True)
    
    class Meta:
        fields = ['application_id', 'feedback_requests']


class InterviewScheduleUpdateSerializer(serializers.Serializer):
    status = serializers.CharField()
    feedback = serializers.CharField(required=False)
    rating = serializers.IntegerField(required=False)
    would_hire = serializers.BooleanField(required=False)
    internal_notes = serializers.CharField(required=False)
    candidate_notes = serializers.CharField(required=False)
