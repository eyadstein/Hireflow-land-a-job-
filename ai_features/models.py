from django.db import models
from django.conf import settings


class CareerRoadmap(models.Model):
    user         = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='roadmaps'
    )
    current_role  = models.CharField(max_length=200)
    target_role   = models.CharField(max_length=200)
    experience    = models.CharField(max_length=100, blank=True)
    skills        = models.TextField(blank=True)
    roadmap       = models.JSONField()
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.current_role} → {self.target_role}"


class CVProfile(models.Model):
    user        = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cvs'
    )
    # Raw input fields
    full_name   = models.CharField(max_length=200)
    email       = models.EmailField()
    phone       = models.CharField(max_length=50, blank=True)
    location    = models.CharField(max_length=200, blank=True)
    title       = models.CharField(max_length=200)
    summary     = models.TextField(blank=True)
    experience  = models.JSONField(default=list)
    education   = models.JSONField(default=list)
    skills      = models.JSONField(default=list)
    languages   = models.JSONField(default=list)

    # AI-enhanced versions (stored separately)
    enhanced_summary    = models.TextField(blank=True)
    enhanced_experience = models.JSONField(default=list)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.title}"