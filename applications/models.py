from django.db import models
from django.conf import settings
from jobs.models import Job


class Application(models.Model):

    KANBAN_STATUS_CHOICES = [
        ('saved',      'Saved'),
        ('applied',    'Applied'),
        ('interview',  'Interview'),
        ('offer',      'Offer'),
        ('rejected',   'Rejected'),
    ]

    # ── Core relations ──────────────────────────────────────────────
    user      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tracker_applications'
    )
    job       = models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='tracker_entries'
    )

    # ── Manual-entry fields (used when no Job FK exists) ────────────
    company_name = models.CharField(max_length=200, blank=True)
    job_title    = models.CharField(max_length=200, blank=True)

    # ── Kanban fields ────────────────────────────────────────────────
    status       = models.CharField(
        max_length=20,
        choices=KANBAN_STATUS_CHOICES,
        default='saved'
    )
    notes        = models.TextField(blank=True)
    applied_date = models.DateField(null=True, blank=True)
    order        = models.PositiveIntegerField(default=0)

    # ── Timestamps ───────────────────────────────────────────────────
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['status', 'order', '-created_at']

    def __str__(self):
        title   = self.job.title if self.job else self.job_title
        company = self.job.company if self.job else self.company_name
        return f"{self.user.username} → {title} @ {company}"

    # ── Helpers ──────────────────────────────────────────────────────
    def get_display_title(self):
        return self.job.title if self.job else self.job_title

    def get_display_company(self):
        return self.job.company if self.job else self.company_name