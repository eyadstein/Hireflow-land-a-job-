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
    

class JobAlert(models.Model):
    FREQUENCY_CHOICES = [
        ('instant', 'Instant'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_alerts'
    )
    keywords = models.CharField(max_length=200)
    country = models.CharField(max_length=50, default='uae')
    experience_level = models.CharField(max_length=50, blank=True)
    job_type = models.CharField(max_length=50, blank=True)
    salary_min = models.FloatField(null=True, blank=True)
    is_remote = models.BooleanField(default=False)
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='daily'
    )
    is_active = models.BooleanField(default=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} → {self.keywords} in {self.country}"


class AlertMatch(models.Model):
    alert = models.ForeignKey(
        JobAlert,
        on_delete=models.CASCADE,
        related_name='matches'
    )
    job_id = models.CharField(max_length=200)
    job_title = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True)
    apply_link = models.URLField(blank=True, null=True)
    matched_at = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)

    class Meta:
        unique_together = ['alert', 'job_id']
        ordering = ['-matched_at']