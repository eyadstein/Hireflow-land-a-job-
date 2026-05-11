from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [('jobseeker', 'Job Seeker'), ('recruiter', 'Recruiter')]
    PLAN_CHOICES = [('free', 'Free'), ('pro', 'Pro')]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='jobseeker')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    public_key = models.TextField(blank=True, null=True)
    fcm_token = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.email