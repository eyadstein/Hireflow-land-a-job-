from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    CandidateProfile, CandidateInteraction, CandidateTask, CandidateDocument,
    CandidatePipeline, CandidatePipelineStage, CandidateTag, CandidateEmail,
    CandidateActivity, CandidateRelationship
)

User = get_user_model()


class CandidateProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)

    class Meta:
        model = CandidateProfile
        fields = [
            'id', 'user', 'user_name', 'user_email', 'status', 'source',
            'source_details', 'assigned_to', 'assigned_to_name', 'tags', 'notes',
            'rating', 'is_active', 'last_contacted', 'next_follow_up',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class CandidateInteractionSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.user.get_full_name', read_only=True)
    candidate_email = serializers.EmailField(source='candidate.user.email', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = CandidateInteraction
        fields = [
            'id', 'candidate', 'candidate_name', 'candidate_email',
            'interaction_type', 'title', 'description', 'date', 'duration_minutes',
            'location', 'attendees', 'outcome', 'next_steps', 'created_by',
            'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class CandidateTaskSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.user.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = CandidateTask
        fields = [
            'id', 'candidate', 'candidate_name', 'title', 'description',
            'status', 'priority', 'due_date', 'completed_date',
            'assigned_to', 'assigned_to_name', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class CandidateDocumentSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.user.get_full_name', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)

    class Meta:
        model = CandidateDocument
        fields = [
            'id', 'candidate', 'candidate_name', 'document_type', 'title',
            'file', 'file_size', 'file_type', 'description', 'is_public',
            'uploaded_by', 'uploaded_by_name', 'uploaded_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'candidate', 'file_size', 'file_type',
            'uploaded_by', 'uploaded_at', 'created_at', 'updated_at'
        ]


class CandidatePipelineSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    candidate_count = serializers.SerializerMethodField()

    class Meta:
        model = CandidatePipeline
        fields = [
            'id', 'name', 'description', 'stages', 'is_active',
            'created_by', 'created_by_name', 'candidate_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_candidate_count(self, obj):
        return obj.candidate_stages.count()


class CandidatePipelineStageSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.user.get_full_name', read_only=True)
    pipeline_name = serializers.CharField(source='pipeline.name', read_only=True)
    moved_by_name = serializers.CharField(source='moved_by.get_full_name', read_only=True)

    class Meta:
        model = CandidatePipelineStage
        fields = [
            'id', 'candidate', 'candidate_name', 'pipeline', 'pipeline_name',
            'stage', 'stage_order', 'entered_at', 'exited_at', 'notes',
            'moved_by', 'moved_by_name'
        ]
        read_only_fields = ['id', 'candidate', 'pipeline', 'entered_at']


class CandidateTagSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = CandidateTag
        fields = [
            'id', 'name', 'color', 'description', 'is_active',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']


class CandidateEmailSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.user.get_full_name', read_only=True)

    class Meta:
        model = CandidateEmail
        fields = [
            'id', 'candidate', 'candidate_name', 'subject', 'content',
            'direction', 'sent_at', 'received_at', 'sender_email',
            'recipient_email', 'is_read', 'thread_id', 'attachments',
            'created_at'
        ]
        read_only_fields = ['id', 'candidate', 'created_at']


class CandidateActivitySerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.user.get_full_name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = CandidateActivity
        fields = [
            'id', 'candidate', 'candidate_name', 'activity_type',
            'description', 'details', 'user', 'user_name',
            'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'candidate', 'user', 'created_at']


class CandidateRelationshipSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.user.get_full_name', read_only=True)
    related_user_name = serializers.CharField(source='related_user.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = CandidateRelationship
        fields = [
            'id', 'candidate', 'candidate_name', 'related_user',
            'related_user_name', 'relationship_type', 'company', 'position',
            'notes', 'is_active', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'candidate', 'related_user', 'created_by',
            'created_at', 'updated_at'
        ]


class CandidateInteractionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateInteraction
        fields = [
            'candidate', 'interaction_type', 'title', 'description',
            'date', 'duration_minutes', 'location', 'attendees',
            'outcome', 'next_steps'
        ]


class CandidateTaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateTask
        fields = [
            'candidate', 'title', 'description', 'status', 'priority',
            'due_date', 'assigned_to'
        ]


class CandidateDocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateDocument
        fields = [
            'candidate', 'document_type', 'title', 'file',
            'description', 'is_public'
        ]


class CandidatePipelineStageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidatePipelineStage
        fields = [
            'candidate', 'pipeline', 'stage', 'stage_order',
            'notes'
        ]


class BulkCandidateTaskSerializer(serializers.Serializer):
    candidates = serializers.ListField(child=serializers.IntegerField())
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    priority = serializers.ChoiceField(choices=CandidateTask.PRIORITY_LEVELS, default='medium')
    due_date = serializers.DateTimeField(required=False)
    assigned_to = serializers.IntegerField(required=False)


class CandidateStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=CandidateProfile.CANDIDATE_STATUS)
    notes = serializers.CharField(required=False)


class CandidateAssignmentSerializer(serializers.Serializer):
    assigned_to = serializers.IntegerField(required=False)
    notes = serializers.CharField(required=False)
