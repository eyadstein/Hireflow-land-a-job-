import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [('jobseeker', 'Job Seeker'), ('recruiter', 'Recruiter')]
    PLAN_CHOICES = [('free', 'Free'), ('pro', 'Pro')]
    GENDER_CHOICES = [('male', 'Male'), ('female', 'Female'), ('other', 'Other')]
    BADGE_CHOICES = [
        ('none', 'No Badge'),
        ('blue', 'Blue - Verified Male'),
        ('pink', 'Pink - Verified Female'),
        ('gold', 'Gold - Pro Verified'),
    ]

    # Basic info
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='jobseeker')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    profile_photo = models.URLField(blank=True, null=True)

    # Keys & tokens
    public_key = models.TextField(blank=True, null=True)
    fcm_token = models.TextField(blank=True, null=True)

    # Job matching profile
    skills = models.JSONField(default=list, blank=True)
    experience_level = models.CharField(max_length=20, default='mid', blank=True)
    desired_roles = models.JSONField(default=list, blank=True)
    preferred_countries = models.JSONField(default=list, blank=True)
    prefers_remote = models.BooleanField(default=False)
    years_of_experience = models.IntegerField(default=0)
    education = models.CharField(max_length=200, blank=True)
    linkedin_url = models.URLField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    resume_url = models.URLField(blank=True, null=True)

    # Verification & badges
    is_profile_verified = models.BooleanField(default=False)
    badge = models.CharField(max_length=10, choices=BADGE_CHOICES, default='none')
    profile_completion = models.IntegerField(default=0)
    verification_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email