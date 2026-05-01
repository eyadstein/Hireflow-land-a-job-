from django.db import models
from django.conf import settings


class Job(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    salary = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class SavedJob(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_jobs'
    )
    job_id = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)
    apply_link = models.URLField(blank=True, null=True)
    salary_min = models.FloatField(null=True, blank=True)
    salary_max = models.FloatField(null=True, blank=True)
    source = models.CharField(max_length=50, blank=True)
    experience_level = models.CharField(max_length=50, blank=True)
    job_type = models.CharField(max_length=50, blank=True)
    logo = models.URLField(blank=True, null=True)
    is_remote = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'job_id']
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.user.username} → {self.title}"