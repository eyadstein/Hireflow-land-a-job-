from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CandidateProfile, JobRequirement, CandidateMatch, MatchingAlgorithm, MatchHistory
from jobs.serializers import JobSerializer

User = get_user_model()


class CandidateProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = CandidateProfile
        fields = [
            'id', 'user', 'user_email', 'user_name', 'skills', 'experience_years',
            'education_level', 'preferred_locations', 'expected_salary_min',
            'expected_salary_max', 'job_types', 'industries', 'resume_text',
            'linkedin_url', 'github_url', 'portfolio_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class JobRequirementSerializer(serializers.ModelSerializer):
    job_details = JobSerializer(source='job', read_only=True)

    class Meta:
        model = JobRequirement
        fields = [
            'id', 'job', 'job_details', 'required_skills', 'experience_required',
            'education_required', 'salary_min', 'salary_max', 'locations',
            'job_types', 'industry', 'description_weighted_keywords',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CandidateMatchSerializer(serializers.ModelSerializer):
    candidate_details = CandidateProfileSerializer(source='candidate', read_only=True)
    job_details = JobSerializer(source='job', read_only=True)

    class Meta:
        model = CandidateMatch
        fields = [
            'id', 'candidate', 'candidate_details', 'job', 'job_details',
            'match_score', 'skill_match_score', 'experience_match_score',
            'education_match_score', 'salary_match_score', 'location_match_score',
            'overall_score', 'match_reasons', 'missing_requirements',
            'is_recommended', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'match_score', 'skill_match_score', 'experience_match_score',
            'education_match_score', 'salary_match_score', 'location_match_score',
            'overall_score', 'match_reasons', 'missing_requirements',
            'is_recommended', 'created_at', 'updated_at'
        ]


class MatchingAlgorithmSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchingAlgorithm
        fields = [
            'id', 'name', 'algorithm_type', 'weights', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MatchHistorySerializer(serializers.ModelSerializer):
    candidate_details = CandidateProfileSerializer(source='candidate', read_only=True)
    job_details = JobSerializer(source='job', read_only=True)

    class Meta:
        model = MatchHistory
        fields = [
            'id', 'candidate', 'candidate_details', 'job', 'job_details',
            'action', 'action_date', 'notes'
        ]
        read_only_fields = ['id', 'candidate', 'job', 'action_date']


class CandidateMatchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateMatch
        fields = ['candidate', 'job']


class MatchHistoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchHistory
        fields = ['candidate', 'job', 'action', 'notes']


class JobMatchingRequestSerializer(serializers.Serializer):
    job_id = serializers.IntegerField()
    limit = serializers.IntegerField(default=10, min_value=1, max_value=100)
    min_score = serializers.FloatField(default=0.0, min_value=0.0, max_value=100.0)


class CandidateMatchingRequestSerializer(serializers.Serializer):
    candidate_id = serializers.IntegerField()
    limit = serializers.IntegerField(default=10, min_value=1, max_value=100)
    min_score = serializers.FloatField(default=0.0, min_value=0.0, max_value=100.0)
    job_types = serializers.ListField(child=serializers.CharField(), required=False)
    locations = serializers.ListField(child=serializers.CharField(), required=False)
    industries = serializers.ListField(child=serializers.CharField(), required=False)
