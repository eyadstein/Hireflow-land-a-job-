from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Job(models.Model):
    title       = models.CharField(max_length=200)
    company     = models.CharField(max_length=200)
    location    = models.CharField(max_length=200)
    salary      = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    posted_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CompanyReview(models.Model):

    EMPLOYMENT_CHOICES = [
        ('full_time',  'Full Time'),
        ('part_time',  'Part Time'),
        ('contract',   'Contract'),
        ('internship', 'Internship'),
        ('interview',  'Interview Experience'),
    ]

    user            = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='company_reviews'
    )
    company         = models.CharField(max_length=200, db_index=True)
    rating          = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title           = models.CharField(max_length=300)
    review          = models.TextField()
    pros            = models.TextField(blank=True)
    cons            = models.TextField(blank=True)
    position        = models.CharField(max_length=200, blank=True)
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_CHOICES,
        default='full_time'
    )
    is_anonymous    = models.BooleanField(default=False)
    helpful_count   = models.PositiveIntegerField(default=0)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering          = ['-created_at']
        unique_together   = ['user', 'company']

    def __str__(self):
        return f"{self.company} — {self.rating}★ by {self.user.username}"


class ReviewHelpful(models.Model):
    user   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='helpful_votes'
    )
    review = models.ForeignKey(
        CompanyReview,
        on_delete=models.CASCADE,
        related_name='helpful_votes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'review']