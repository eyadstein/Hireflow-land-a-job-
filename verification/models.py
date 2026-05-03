from django.db import models
from django.conf import settings


class ProfileVerification(models.Model):
    STATUS_CHOICES = [
        ('incomplete', 'Incomplete'),
        ('pending', 'Pending Review'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='verification'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='incomplete'
    )
    completion_percentage = models.IntegerField(default=0)

    # Required fields checklist
    has_name = models.BooleanField(default=False)
    has_email = models.BooleanField(default=False)
    has_phone = models.BooleanField(default=False)
    has_location = models.BooleanField(default=False)
    has_bio = models.BooleanField(default=False)
    has_skills = models.BooleanField(default=False)
    has_experience_level = models.BooleanField(default=False)
    has_education = models.BooleanField(default=False)
    has_desired_roles = models.BooleanField(default=False)
    has_gender = models.BooleanField(default=False)

    # Optional but boost score
    has_profile_photo = models.BooleanField(default=False)
    has_linkedin = models.BooleanField(default=False)
    has_resume = models.BooleanField(default=False)
    has_portfolio = models.BooleanField(default=False)

    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.status} ({self.completion_percentage}%)"