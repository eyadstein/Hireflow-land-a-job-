from django.db import models
from django.conf import settings


class CareerRoadmap(models.Model):
    user         = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='roadmaps'
    )
    current_role = models.CharField(max_length=200)
    target_role  = models.CharField(max_length=200)
    experience   = models.CharField(max_length=100, blank=True)
    skills       = models.TextField(blank=True)
    roadmap      = models.JSONField()
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.current_role} → {self.target_role}"


class CVProfile(models.Model):
    user                = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cvs'
    )
    full_name           = models.CharField(max_length=200)
    email               = models.EmailField()
    phone               = models.CharField(max_length=50, blank=True)
    location            = models.CharField(max_length=200, blank=True)
    title               = models.CharField(max_length=200)
    summary             = models.TextField(blank=True)
    experience          = models.JSONField(default=list)
    education           = models.JSONField(default=list)
    skills              = models.JSONField(default=list)
    languages           = models.JSONField(default=list)
    enhanced_summary    = models.TextField(blank=True)
    enhanced_experience = models.JSONField(default=list)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.title}"


class MockInterviewSession(models.Model):
    user             = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interview_sessions'
    )
    role             = models.CharField(max_length=200)
    level            = models.CharField(max_length=50, default='Mid')
    questions        = models.JSONField()
    overall_score    = models.IntegerField(null=True, blank=True)
    overall_feedback = models.TextField(blank=True)
    completed        = models.BooleanField(default=False)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.role} ({self.level})"


class MockInterviewAnswer(models.Model):
    session       = models.ForeignKey(
        MockInterviewSession,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question      = models.TextField()
    question_type = models.CharField(max_length=50, default='technical')
    user_answer   = models.TextField()
    score         = models.IntegerField(null=True, blank=True)
    grade         = models.CharField(max_length=10, blank=True)
    feedback      = models.TextField(blank=True)
    ideal_answer  = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer for session {self.session.id} — score: {self.score}"


class LinkedInOptimization(models.Model):
    user          = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='linkedin_optimizations'
    )
    headline      = models.CharField(max_length=500, blank=True)
    about         = models.TextField(blank=True)
    experience    = models.TextField(blank=True)
    skills        = models.JSONField(default=list)
    target_role   = models.CharField(max_length=200, blank=True)
    profile_score = models.IntegerField(null=True, blank=True)
    optimized     = models.JSONField()
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — LinkedIn optimization ({self.profile_score}/100)"


class CareerIntelligenceReport(models.Model):

    REPORT_TYPES = [
        ('career_path',  'Career Path Predictor'),
        ('skill_gap',    'Skill Gap Analyzer'),
        ('market_trends','Market Trends'),
        ('resume_gap',   'Resume vs Job Gap'),
        ('competitor',   'Competitor Analysis'),
    ]

    user        = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='intelligence_reports'
    )
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    input_data  = models.JSONField(default=dict)
    report      = models.JSONField()
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.report_type} ({self.created_at.strftime('%Y-%m-%d')})"