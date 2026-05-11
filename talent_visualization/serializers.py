from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    TalentPool, TalentPoolCandidate, TalentVisualization, TalentAnalytics,
    TalentDashboard, UserDashboard, TalentReport, ReportSchedule, TalentInsight
)

User = get_user_model()


class TalentPoolSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    candidate_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TalentPool
        fields = [
            'id', 'name', 'description', 'pool_type', 'job_category',
            'skills', 'experience_levels', 'locations', 'is_active',
            'created_by', 'created_by_name', 'candidate_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by_name', 'candidate_count']
    
    def get_candidate_count(self, obj):
        return obj.candidates.count()


class TalentPoolCandidateSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.get_full_name', read_only=True)
    talent_pool_name = serializers.CharField(source='talent_pool.name', read_only=True)
    
    class Meta:
        model = TalentPoolCandidate
        fields = [
            'id', 'talent_pool', 'talent_pool_name', 'candidate', 'candidate_name',
            'status', 'skills', 'experience_years', 'education_level',
            'location', 'salary_expectation', 'availability', 'notes',
            'last_contacted', 'added_at', 'updated_at'
        ]
        read_only_fields = ['candidate_name', 'talent_pool_name']


class TalentVisualizationSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = TalentVisualization
        fields = [
            'id', 'name', 'chart_type', 'description', 'configuration',
            'data', 'filters', 'is_public', 'is_active',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by_name']


class TalentAnalyticsSerializer(serializers.ModelSerializer):
    pool_name = serializers.CharField(source='talent_pool.name', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    visualization_name = serializers.CharField(source='visualization.name', read_only=True)
    
    class Meta:
        model = TalentAnalytics
        fields = [
            'id', 'metric_type', 'value', 'metadata', 'date',
            'talent_pool', 'pool_name', 'job', 'job_title',
            'visualization', 'visualization_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['pool_name', 'job_title', 'visualization_name']


class TalentDashboardSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = TalentDashboard
        fields = [
            'id', 'name', 'dashboard_type', 'description', 'layout',
            'widgets', 'filters', 'refresh_interval', 'is_public',
            'is_active', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by_name']


class UserDashboardSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    dashboard_name = serializers.CharField(source='dashboard.name', read_only=True)
    
    class Meta:
        model = UserDashboard
        fields = [
            'id', 'user', 'user_name', 'dashboard', 'dashboard_name',
            'is_favorite', 'custom_filters', 'custom_layout',
            'last_accessed', 'created_at'
        ]
        read_only_fields = ['user_name', 'dashboard_name']


class TalentReportSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = TalentReport
        fields = [
            'id', 'name', 'report_type', 'description', 'template',
            'data', 'filters', 'format', 'is_scheduled',
            'schedule_frequency', 'last_generated', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by_name']


class ReportScheduleSerializer(serializers.ModelSerializer):
    report_name = serializers.CharField(source='report.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ReportSchedule
        fields = [
            'id', 'report', 'report_name', 'recipients', 'frequency',
            'next_run', 'is_active', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['report_name', 'created_by_name']


class TalentInsightSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = TalentInsight
        fields = [
            'id', 'title', 'insight_type', 'description', 'data_points',
            'confidence_score', 'impact_level', 'action_items', 'is_active',
            'expires_at', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by_name']


# Create serializers
class TalentPoolCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalentPool
        fields = ['name', 'description', 'pool_type', 'job_category', 'skills', 'experience_levels', 'locations']


class TalentPoolCandidateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalentPoolCandidate
        fields = [
            'talent_pool', 'candidate', 'skills', 'experience_years',
            'education_level', 'location', 'salary_expectation',
            'availability', 'notes'
        ]


class TalentVisualizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalentVisualization
        fields = ['name', 'chart_type', 'description', 'configuration', 'data', 'filters', 'is_public']


class TalentAnalyticsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalentAnalytics
        fields = ['metric_type', 'value', 'metadata', 'date', 'talent_pool', 'job', 'visualization']


class TalentDashboardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalentDashboard
        fields = ['name', 'dashboard_type', 'description', 'layout', 'widgets', 'filters', 'refresh_interval', 'is_public']


class UserDashboardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDashboard
        fields = ['user', 'dashboard', 'is_favorite', 'custom_filters', 'custom_layout']


class TalentReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalentReport
        fields = ['name', 'report_type', 'description', 'template', 'data', 'filters', 'format', 'is_scheduled', 'schedule_frequency']


class ReportScheduleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSchedule
        fields = ['report', 'recipients', 'frequency', 'next_run']


class TalentInsightCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalentInsight
        fields = ['title', 'insight_type', 'description', 'data_points', 'confidence_score', 'impact_level', 'action_items', 'expires_at']


# Bulk operations serializers
class BulkAddCandidatesSerializer(serializers.Serializer):
    talent_pool_id = serializers.IntegerField()
    candidates = TalentPoolCandidateCreateSerializer(many=True)
    
    class Meta:
        fields = ['talent_pool_id', 'candidates']


class BulkAnalyticsSerializer(serializers.Serializer):
    analytics_data = TalentAnalyticsCreateSerializer(many=True)
    
    class Meta:
        fields = ['analytics_data']


class DashboardLayoutSerializer(serializers.Serializer):
    layout = serializers.JSONField()
    widgets = serializers.JSONField()
    filters = serializers.JSONField()
    
    class Meta:
        fields = ['layout', 'widgets', 'filters']
