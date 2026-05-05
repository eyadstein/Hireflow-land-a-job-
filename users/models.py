from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = [('jobseeker', 'Job Seeker'), ('recruiter', 'Recruiter')]
    PLAN_CHOICES = [('free', 'Free'), ('pro', 'Pro')]

    role       = models.CharField(max_length=20, choices=ROLE_CHOICES, default='jobseeker')
    plan       = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    public_key = models.TextField(blank=True, null=True)
    fcm_token  = models.TextField(blank=True, null=True)

    # 2FA
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret  = models.CharField(max_length=64, blank=True)

    # Brute force protection
    failed_login_attempts = models.IntegerField(default=0)
    lockout_until         = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email

    def is_locked_out(self):
        if self.lockout_until and timezone.now() < self.lockout_until:
            return True
        return False

    def record_failed_login(self):
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.lockout_until         = timezone.now() + timezone.timedelta(minutes=15)
            self.failed_login_attempts = 0
        self.save(update_fields=['failed_login_attempts', 'lockout_until'])

    def reset_failed_login(self):
        self.failed_login_attempts = 0
        self.lockout_until         = None
        self.save(update_fields=['failed_login_attempts', 'lockout_until'])


class BlacklistedToken(models.Model):
    token      = models.TextField(unique=True)
    user       = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='blacklisted_tokens'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Blacklisted token for {self.user.username}"


class SecurityAuditLog(models.Model):

    EVENT_CHOICES = [
        ('login',          'Login'),
        ('logout',         'Logout'),
        ('login_failed',   'Login Failed'),
        ('locked_out',     'Account Locked Out'),
        ('2fa_enabled',    '2FA Enabled'),
        ('2fa_disabled',   '2FA Disabled'),
        ('2fa_verified',   '2FA Verified'),
        ('password_change','Password Changed'),
        ('profile_update', 'Profile Updated'),
        ('token_refresh',  'Token Refreshed'),
    ]

    user       = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='audit_logs',
        null=True, blank=True
    )
    event      = models.CharField(max_length=50, choices=EVENT_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    details    = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event} — {self.user.username if self.user else 'anonymous'} @ {self.created_at}"


class TwoFactorCode(models.Model):
    user       = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='two_factor_codes'
    )
    code       = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    used       = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at

    def __str__(self):
        return f"2FA code for {self.user.username}"