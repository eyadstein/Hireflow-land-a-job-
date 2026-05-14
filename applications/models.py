from django.db import models
from django.conf import settings


class Application(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("applied", "Applied"),
        ("screening", "Screening"),
        ("interview", "Interview"),
        ("offer", "Offer"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("withdrawn", "Withdrawn"),
    ]

    job = models.ForeignKey(
        "jobs.Job",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications",
    )

    job_title = models.CharField(max_length=200, blank=True, default="")
    company = models.CharField(max_length=200, blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    applied_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    contact_name = models.CharField(max_length=100, blank=True, default="")
    contact_email = models.CharField(max_length=200, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["job", "status"]),
            models.Index(fields=["applicant", "status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["reviewed_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["job", "applicant"],
                name="unique_application_per_job_applicant",
                condition=models.Q(job__isnull=False),
            )
        ]

    def save(self, *args, **kwargs):
        if self.job:
            if not self.job_title:
                self.job_title = self.job.title
            if not self.company:
                self.company = self.job.company

        super().save(*args, **kwargs)

    def __str__(self):
        if self.job:
            return f"{self.applicant.username} → {self.job.title}"
        return f"{self.applicant.username} → {self.job_title} at {self.company}"


class CandidateNote(models.Model):
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_notes",
    )

    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="written_notes",
    )

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["candidate", "recruiter"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Note by {self.recruiter.username} on {self.candidate.username}"