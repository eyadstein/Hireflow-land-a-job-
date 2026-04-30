from django.db import models
from django.conf import settings

class JobSeekerProfile(models.Model):
    """Profile data for job seekers - links to the main User model"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_seeker_profile'
    )
    
    # Job matching profile fields
    skills = models.JSONField(default=list, blank=True)
    experience_level = models.CharField(max_length=20, default='mid', blank=True)
    desired_roles = models.JSONField(default=list, blank=True)
    preferred_countries = models.JSONField(default=list, blank=True)
    prefers_remote = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True)
    
    # Optional: add these if you really need them in this model
    role = models.CharField(max_length=20, choices=[('jobseeker', 'Job Seeker'), ('recruiter', 'Recruiter')], default='jobseeker')
    plan = models.CharField(max_length=20, choices=[('free', 'Free'), ('pro', 'Pro')], default='free')
    public_key = models.TextField(blank=True, null=True)
    fcm_token = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.email}'s profile"