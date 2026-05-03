import random
import string
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


class OTP(models.Model):
    TYPE_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
    ]
    PURPOSE_CHOICES = [
        ('verify', 'Verification'),
        ('reset', 'Password Reset'),
        ('login', 'Login'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='otps'
    )
    code = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES, default='verify')
    is_used = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_otp()
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(
                minutes=settings.OTP_EXPIRY_MINUTES
            )
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.user.username} - {self.otp_type} - {self.code}"