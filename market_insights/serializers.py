from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    MarketData, SalaryInsight, DemandAnalysis, SkillsAnalysis,
    MarketTrend, CompensationBenchmark, MarketReport, ReportSubscription, MarketAlert
)

User = get_user_model()


class MarketDataSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = MarketData
        fields = [
            'id', 'data_type', 'job_category', 'job_title', 'location',
            'industry', 'experience_level', 'data_value', 'source',
            'collection_date', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by_name']


class SalaryInsightSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = SalaryInsight
        fields = [
            'id', 'job_title', 'job_category', 'experience_level', 'location',
            'insight_type', 'salary_data', 'min_salary', 'max_salary',
            'median_salary', 'mean_salary', 'percentile_25', 'percentile_75',
            'currency', 'data_points', 'confidence_level', 'last_updated',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by_name']


class DemandAnalysisSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = DemandAnalysis
        fields = [
            'id', 'job_category', 'job_title', 'location', 'demand_level',
            'demand_score', 'job_postings', 'active_candidates',
            'hiring_velocity', 'time_to_fill', 'growth_rate',
            'competition_level', 'analysis_date', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by_name']


class SkillsAnalysisSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = SkillsAnalysis
        fields = [
            'id', 'skill_name', 'skill_type', 'job_categories', 'demand_level',
            'growth_trend', 'salary_impact', 'market_saturation',
            'learning_time', 'analysis_date', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by_name']


class MarketTrendSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = MarketTrend
        fields = [
            'id', 'trend_type', 'category', 'title', 'trend_data',
            'trend_direction', 'change_percentage', 'confidence_interval',
            'prediction_period', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by_name']


class CompensationBenchmarkSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = CompensationBenchmark
        fields = [
            'id', 'job', 'job_title', 'benchmark_type', 'benchmark_category',
            'base_salary_min', 'base_salary_max', 'base_salary_median',
            'total_comp_min', 'total_comp_max', 'total_comp_median',
            'bonus_percentage', 'equity_range', 'benefits_value',
            'currency', 'sample_size', 'data_quality_score', 'last_updated',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['job_title', 'created_by_name']


class MarketReportSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = MarketReport
        fields = [
            'id', 'name', 'report_type', 'description', 'parameters',
            'data', 'insights', 'recommendations', 'format',
            'is_public', 'is_scheduled', 'schedule_frequency',
            'last_generated', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by_name']


class ReportSubscriptionSerializer(serializers.ModelSerializer):
    report_name = serializers.CharField(source='report.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ReportSubscription
        fields = [
            'id', 'report', 'report_name', 'subscribers', 'frequency',
            'next_delivery', 'is_active', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['report_name', 'created_by_name']


class MarketAlertSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = MarketAlert
        fields = [
            'id', 'title', 'alert_type', 'description', 'severity',
            'affected_roles', 'affected_locations', 'trigger_conditions',
            'action_required', 'action_items', 'expires_at', 'is_active',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by_name']


# Create serializers
class MarketDataCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketData
        fields = [
            'data_type', 'job_category', 'job_title', 'location',
            'industry', 'experience_level', 'data_value', 'source',
            'collection_date', 'is_active'
        ]


class SalaryInsightCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryInsight
        fields = [
            'job_title', 'job_category', 'experience_level', 'location',
            'insight_type', 'salary_data', 'min_salary', 'max_salary',
            'median_salary', 'mean_salary', 'percentile_25', 'percentile_75',
            'currency', 'data_points', 'confidence_level', 'last_updated'
        ]


class DemandAnalysisCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandAnalysis
        fields = [
            'job_category', 'job_title', 'location', 'demand_level',
            'demand_score', 'job_postings', 'active_candidates',
            'hiring_velocity', 'time_to_fill', 'growth_rate',
            'competition_level', 'analysis_date'
        ]


class SkillsAnalysisCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillsAnalysis
        fields = [
            'skill_name', 'skill_type', 'job_categories', 'demand_level',
            'growth_trend', 'salary_impact', 'market_saturation',
            'learning_time', 'analysis_date'
        ]


class MarketTrendCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketTrend
        fields = [
            'trend_type', 'category', 'title', 'trend_data',
            'trend_direction', 'change_percentage', 'confidence_interval',
            'prediction_period'
        ]


class CompensationBenchmarkCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompensationBenchmark
        fields = [
            'job', 'benchmark_type', 'benchmark_category',
            'base_salary_min', 'base_salary_max', 'base_salary_median',
            'total_comp_min', 'total_comp_max', 'total_comp_median',
            'bonus_percentage', 'equity_range', 'benefits_value',
            'currency', 'sample_size', 'data_quality_score', 'last_updated'
        ]


class MarketReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketReport
        fields = [
            'name', 'report_type', 'description', 'parameters',
            'data', 'insights', 'recommendations', 'format',
            'is_public', 'is_scheduled', 'schedule_frequency'
        ]


class ReportSubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSubscription
        fields = ['report', 'subscribers', 'frequency', 'next_delivery', 'is_active']


class MarketAlertCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketAlert
        fields = [
            'title', 'alert_type', 'description', 'severity',
            'affected_roles', 'affected_locations', 'trigger_conditions',
            'action_required', 'action_items', 'expires_at', 'is_active'
        ]


# Bulk operations serializers
class BulkMarketDataSerializer(serializers.Serializer):
    market_data = MarketDataCreateSerializer(many=True)
    
    class Meta:
        fields = ['market_data']


class BulkSalaryInsightSerializer(serializers.Serializer):
    salary_insights = SalaryInsightCreateSerializer(many=True)
    
    class Meta:
        fields = ['salary_insights']


class SalaryComparisonSerializer(serializers.Serializer):
    job_title = serializers.CharField(max_length=200)
    location = serializers.CharField(max_length=200)
    experience_level = serializers.CharField(max_length=50, required=False)
    currency = serializers.CharField(max_length=3, default='USD')
    
    class Meta:
        fields = ['job_title', 'location', 'experience_level', 'currency']


class DemandAnalysisSerializer(serializers.Serializer):
    job_category = serializers.CharField(max_length=100)
    location = serializers.CharField(max_length=200)
    time_period = serializers.IntegerField(default=30)  # days
    
    class Meta:
        fields = ['job_category', 'location', 'time_period']


class SkillsGapAnalysisSerializer(serializers.Serializer):
    required_skills = serializers.ListField(child=serializers.CharField())
    job_category = serializers.CharField(max_length=100)
    location = serializers.CharField(max_length=200)
    
    class Meta:
        fields = ['required_skills', 'job_category', 'location']


class MarketTrendAnalysisSerializer(serializers.Serializer):
    trend_type = serializers.ChoiceField(choices=MarketTrend.TREND_TYPES)
    category = serializers.CharField(max_length=100)
    time_period = serializers.IntegerField(default=12)  # months
    
    class Meta:
        fields = ['trend_type', 'category', 'time_period']


class CompensationAnalysisSerializer(serializers.Serializer):
    job_id = serializers.IntegerField()
    benchmark_types = serializers.ListField(child=serializers.CharField())
    locations = serializers.ListField(child=serializers.CharField(), required=False)
    experience_levels = serializers.ListField(child=serializers.CharField(), required=False)
    
    class Meta:
        fields = ['job_id', 'benchmark_types', 'locations', 'experience_levels']
