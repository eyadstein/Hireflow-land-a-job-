from django.db import models
from django.conf import settings


class Application(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('screening', 'Screening'),
        ('interview', 'Interview'),
        ('offer', 'Offer'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]

    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tracked_applications',
    )
    job_title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    applied_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    contact_name = models.CharField(max_length=100, blank=True, default='')
    contact_email = models.CharField(max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.applicant.username} → {self.job_title} at {self.company}"
