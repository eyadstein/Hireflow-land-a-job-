from django.db import models
from django.conf import settings


class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
        ('on_site', 'On-site'),
        ('hybrid', 'Hybrid'),
    ]

    DEPT_CHOICES = [
        ('engineering', 'Engineering'),
        ('design', 'Design'),
        ('marketing', 'Marketing'),
        ('sales', 'Sales'),
        ('operations', 'Operations'),
        ('hr', 'HR'),
        ('finance', 'Finance'),
        ('product', 'Product'),
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

    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True, default='')
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    department = models.CharField(max_length=20, choices=DEPT_CHOICES, blank=True, default='')
    description = models.TextField()
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    url = models.URLField(blank=True, default='')
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    career_level = models.CharField(max_length=20, choices=CAREER_LEVEL_CHOICES, blank=True)
    category = models.CharField(max_length=100, blank=True)
    requirements = models.TextField(blank=True)
    years_experience = models.CharField(max_length=50, blank=True)
    education = models.CharField(max_length=200, blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='recruiter')

    is_filled = models.BooleanField(default=False)
    filled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
