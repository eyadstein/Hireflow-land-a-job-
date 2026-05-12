from django.db import models
from django.contrib.auth import get_user_model
from jobs.models import Job

User = get_user_model()


class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    skills = models.JSONField(default=list)
    experience_years = models.FloatField(default=0)
    education_level = models.CharField(max_length=50, choices=[
        ('high_school', 'High School'),
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('phd', 'PhD'),
    ], default='bachelor')
    preferred_locations = models.JSONField(default=list)
    expected_salary_min = models.IntegerField(null=True, blank=True)
    expected_salary_max = models.IntegerField(null=True, blank=True)
    job_types = models.JSONField(default=list)
    industries = models.JSONField(default=list)
    resume_text = models.TextField(blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - Candidate Profile"


class JobRequirement(models.Model):
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name='requirements')
    required_skills = models.JSONField(default=list)
    experience_required = models.FloatField(default=0)
    education_required = models.CharField(max_length=50, choices=[
        ('high_school', 'High School'),
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('phd', 'PhD'),
    ], default='bachelor')
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    locations = models.JSONField(default=list)
    job_types = models.JSONField(default=list)
    industry = models.CharField(max_length=100, blank=True)
    description_weighted_keywords = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job.title} - Requirements"


class CandidateMatch(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='matches')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='candidate_matches')
    match_score = models.FloatField(default=0.0)
    skill_match_score = models.FloatField(default=0.0)
    experience_match_score = models.FloatField(default=0.0)
    education_match_score = models.FloatField(default=0.0)
    salary_match_score = models.FloatField(default=0.0)
    location_match_score = models.FloatField(default=0.0)
    overall_score = models.FloatField(default=0.0)
    match_reasons = models.JSONField(default=list)
    missing_requirements = models.JSONField(default=list)
    is_recommended = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['candidate', 'job']
        ordering = ['-overall_score']

    def __str__(self):
        return f"{self.candidate.user.email} - {self.job.title} ({self.overall_score}%)"


class MatchingAlgorithm(models.Model):
    name = models.CharField(max_length=100, unique=True)
    algorithm_type = models.CharField(max_length=50, choices=[
        ('keyword', 'Keyword Based'),
        ('ml', 'Machine Learning'),
        ('hybrid', 'Hybrid'),
    ], default='hybrid')
    weights = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.algorithm_type})"


class MatchHistory(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='match_history')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='match_history')
    action = models.CharField(max_length=20, choices=[
        ('viewed', 'Viewed'),
        ('applied', 'Applied'),
        ('saved', 'Saved'),
        ('rejected', 'Rejected'),
        ('interviewed', 'Interviewed'),
        ('hired', 'Hired'),
    ])
    action_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-action_date']

    def __str__(self):
        return f"{self.candidate.user.email} - {self.action} - {self.job.title}"
