from django.db import models
from django.conf import settings


class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('Remote', 'Remote'),
        ('On-site', 'On-site'),
        ('Hybrid', 'Hybrid'),
    ]

    CAREER_LEVEL_CHOICES = [
        ('Entry Level', 'Entry Level'),
        ('Mid Level', 'Mid Level'),
        ('Senior', 'Senior'),
        ('Lead', 'Lead'),
        ('Manager', 'Manager'),
    ]

    SOURCE_CHOICES = [
        ('recruiter', 'Recruiter'),
        ('seed', 'Seed'),
        ('scraped', 'Scraped'),
    ]

    # ── Core fields (Eyad's original) ──
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    salary = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    # ── Extended fields (for Mohaned's AI processing) ──
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, blank=True)
    career_level = models.CharField(max_length=20, choices=CAREER_LEVEL_CHOICES, blank=True)
    category = models.CharField(max_length=100, blank=True)
    requirements = models.TextField(blank=True)
    years_experience = models.CharField(max_length=50, blank=True)
    education = models.CharField(max_length=200, blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='recruiter')

    def __str__(self):
        return self.title
