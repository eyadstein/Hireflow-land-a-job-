from django.db import models
from django.conf import settings
from django.utils import timezone


class PlanLimit(models.Model):
    """Defines limits for each plan."""
    PLAN_CHOICES = [('free', 'Free'), ('pro', 'Pro')]

    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, unique=True)
    ai_uses_per_day = models.IntegerField(default=5)
    saved_jobs_limit = models.IntegerField(default=10)
    alerts_limit = models.IntegerField(default=2)
    can_see_salary = models.BooleanField(default=False)
    can_use_interview_coach = models.BooleanField(default=False)
    can_use_cv_builder = models.BooleanField(default=False)

    def __str__(self):
        return self.plan


class UsageTracker(models.Model):
    """Tracks daily AI usage per user."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='usage'
    )
    feature = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now)
    count = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'feature', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.feature} - {self.date}: {self.count}"


class PlanUpgradeRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='upgrade_requests'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    payment_reference = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.status}"