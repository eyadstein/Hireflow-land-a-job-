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
    roadmap       = models.JSONField()        # stores full Gemini response
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.current_role} → {self.target_role}"