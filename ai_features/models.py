from django.db import models
from django.conf import settings


# ── Step 7 — Career Roadmap ──────────────────────────────────────────
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


# ── Step 8 — CV Builder ──────────────────────────────────────────────
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


# ── Step 9 — Mock Interview ──────────────────────────────────────────
class MockInterviewSession(models.Model):
    user       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interview_sessions'
    )
    role       = models.CharField(max_length=200)
    level      = models.CharField(max_length=50, default='Mid')
    questions  = models.JSONField()         # list of generated questions
    overall_score    = models.IntegerField(null=True, blank=True)
    overall_feedback = models.TextField(blank=True)
    completed  = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.role} ({self.level})"


class MockInterviewAnswer(models.Model):
    session      = models.ForeignKey(
        MockInterviewSession,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question     = models.TextField()
    question_type = models.CharField(max_length=50, default='technical')
    user_answer  = models.TextField()
    score        = models.IntegerField(null=True, blank=True)
    grade        = models.CharField(max_length=10, blank=True)
    feedback     = models.TextField(blank=True)
    ideal_answer = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer for session {self.session.id} — score: {self.score}"