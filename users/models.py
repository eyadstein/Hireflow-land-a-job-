from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ("jobseeker", "Job Seeker"),
        ("student", "Student"),
        ("recruiter", "Recruiter"),
        ("company", "Company"),
        ("admin", "Admin"),
    ]

    PLAN_CHOICES = [
        ("free", "Free"),
        ("pro", "Pro"),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ("", "Not specified"),
        ("student", "Student"),
        ("intern", "Intern"),
        ("junior", "Junior"),
        ("mid", "Mid-level"),
        ("senior", "Senior"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="jobseeker",
    )

    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default="free",
    )

    public_key = models.TextField(blank=True, null=True)
    fcm_token = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, default='')
    skills = models.TextField(blank=True, default='')
    experience_level = models.CharField(max_length=50, blank=True, default='')
    desired_roles = models.TextField(blank=True, default='')
    preferred_countries = models.TextField(blank=True, default='')
    prefers_remote = models.BooleanField(default=False)
    city = models.CharField(max_length=100, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='Egypt')
    linkedin = models.URLField(blank=True, default='')
    portfolio = models.URLField(blank=True, default='')

    bio = models.TextField(blank=True, default="")
    skills = models.TextField(blank=True, default="")
    experience_level = models.CharField(
        max_length=50,
        choices=EXPERIENCE_LEVEL_CHOICES,
        blank=True,
        default="",
    )

    desired_roles = models.TextField(blank=True, default="")
    preferred_countries = models.TextField(blank=True, default="")
    prefers_remote = models.BooleanField(default=False)

    city = models.CharField(max_length=100, blank=True, default="")
    country = models.CharField(max_length=100, blank=True, default="Egypt")
    linkedin = models.URLField(blank=True, default="")
    portfolio = models.URLField(blank=True, default="")

    def __str__(self):
        return self.email or self.username