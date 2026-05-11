from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    TalentPool, TalentCandidate, TalentSearch, TalentEngagement,
    TalentCampaign, TalentCampaignExecution, TalentInsight,
    TalentSource, TalentSourcingRule, TalentAnalytics
)

User = get_user_model()


class TalentPoolSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    candidate_count = serializers.SerializerMethodField()

    class Meta:
        model = TalentPool
        fields = [
            'id', 'name', 'description', 'pool_type', 'criteria', 'is_active',
            'created_by', 'created_by_name', 'candidate_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_candidate_count(self, obj):
        return obj.candidates.count()


class TalentCandidateSerializer(serializers.ModelSerializer):
    pool_name = serializers.CharField(source='pool.name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = TalentCandidate
        fields = [
            'id', 'pool', 'pool_name', 'user', 'user_name', 'user_email',
            'first_name', 'last_name', 'email', 'phone', 'location', 'country',
            'title', 'company', 'industry', 'experience_years', 'skills',
            'education', 'linkedin_url', 'github_url', 'portfolio_url',
            'twitter_url', 'personal_website', 'source', 'source_details',
            'discovered_at', 'last_contacted', 'status', 'is_active',
            'is_interested', 'response_rate', 'notes', 'tags',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'pool', 'user', 'discovered_at', 'created_at', 'updated_at']


class TalentSearchSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = TalentSearch
        fields = [
            'id', 'name', 'search_type', 'query', 'filters',
            'results_count', 'is_saved', 'created_by', 'created_by_name',
            'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']


class TalentEngagementSerializer(serializers.ModelSerializer):
    candidate_name = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = TalentEngagement
        fields = [
            'id', 'candidate', 'candidate_name', 'engagement_type',
            'status', 'subject', 'message', 'template_used',
            'sent_at', 'opened_at', 'replied_at', 'response',
            'next_action', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'candidate', 'created_by', 'created_at', 'updated_at']

    def get_candidate_name(self, obj):
        return f"{obj.candidate.first_name} {obj.candidate.last_name}"


class TalentCampaignSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    target_pools_info = TalentPoolSerializer(source='target_pools', many=True, read_only=True)

    class Meta:
        model = TalentCampaign
        fields = [
            'id', 'name', 'description', 'campaign_type', 'status',
            'target_pools', 'target_pools_info', 'target_criteria',
            'subject', 'message_template', 'personalization_vars',
            'start_date', 'end_date', 'send_immediately',
            'total_sent', 'total_opened', 'total_replied', 'total_interested',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_by', 'total_sent', 'total_opened',
            'total_replied', 'total_interested', 'created_at', 'updated_at'
        ]


class TalentCampaignExecutionSerializer(serializers.ModelSerializer):
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)
    candidate_name = serializers.SerializerMethodField()

    class Meta:
        model = TalentCampaignExecution
        fields = [
            'id', 'campaign', 'campaign_name', 'candidate', 'candidate_name',
            'sent_at', 'status', 'personalized_subject',
            'personalized_message', 'opened_at', 'replied_at',
            'response', 'tracking_id', 'opened_count', 'clicked_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'campaign', 'candidate', 'tracking_id',
            'created_at', 'updated_at'
        ]

    def get_candidate_name(self, obj):
        return f"{obj.candidate.first_name} {obj.candidate.last_name}"


class TalentInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalentInsight
        fields = [
            'id', 'insight_type', 'title', 'description', 'data',
            'confidence_score', 'generated_at', 'valid_until',
            'source', 'is_active', 'is_verified',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'generated_at', 'created_at', 'updated_at']


class TalentSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalentSource
        fields = [
            'id', 'name', 'source_type', 'base_url', 'api_endpoint',
            'api_key', 'api_secret', 'is_active', 'requests_per_hour',
            'requests_per_day', 'search_config', 'field_mapping',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TalentSourcingRuleSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = TalentSourcingRule
        fields = [
            'id', 'name', 'rule_type', 'conditions', 'actions',
            'is_active', 'run_frequency', 'last_run', 'next_run',
            'candidates_found', 'candidates_added', 'created_by',
            'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_by', 'last_run', 'candidates_found',
            'candidates_added', 'created_at', 'updated_at'
        ]


class TalentAnalyticsSerializer(serializers.ModelSerializer):
    pool_name = serializers.CharField(source='pool.name', read_only=True)
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)
    source_name = serializers.CharField(source='source.name', read_only=True)

    class Meta:
        model = TalentAnalytics
        fields = [
            'id', 'metric_type', 'date', 'value', 'metadata',
            'pool', 'pool_name', 'campaign', 'campaign_name',
            'source', 'source_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# Create serializers
class TalentPoolCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalentPool
        fields = ['name', 'description', 'pool_type', 'criteria', 'is_active']


class TalentCandidateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalentCandidate
        fields = [
            'pool', 'first_name', 'last_name', 'email', 'phone',
            'location', 'country', 'title', 'company', 'industry',
            'experience_years', 'skills', 'education', 'linkedin_url',
            'github_url', 'portfolio_url', 'twitter_url',
            'personal_website', 'source', 'source_details', 'status',
            'is_active', 'is_interested', 'notes', 'tags'
        ]


class TalentEngagementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalentEngagement
        fields = [
            'candidate', 'engagement_type', 'subject', 'message',
            'template_used'
        ]


class TalentCampaignCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalentCampaign
        fields = [
            'name', 'description', 'campaign_type', 'target_pools',
            'target_criteria', 'subject', 'message_template',
            'personalization_vars', 'start_date', 'end_date',
            'send_immediately'
        ]


class TalentSearchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalentSearch
        fields = ['name', 'search_type', 'query', 'filters', 'is_saved']


class BulkCandidateAddSerializer(serializers.Serializer):
    pool_id = serializers.IntegerField()
    candidates = serializers.ListField(child=serializers.DictField())
    source = serializers.CharField(max_length=20)
    source_details = serializers.CharField(required=False)


class TalentCampaignLaunchSerializer(serializers.Serializer):
    campaign_id = serializers.IntegerField()
    send_immediately = serializers.BooleanField(default=False)


class CandidateSearchRequestSerializer(serializers.Serializer):
    query = serializers.CharField()
    search_type = serializers.CharField()
    filters = serializers.JSONField(default=dict)
    limit = serializers.IntegerField(default=50)
    offset = serializers.IntegerField(default=0)


class TalentInsightGenerateSerializer(serializers.Serializer):
    insight_type = serializers.CharField()
    parameters = serializers.JSONField(default=dict)
    date_range = serializers.JSONField(default=dict)
