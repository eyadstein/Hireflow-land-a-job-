from django.db import models
from django.contrib.auth import get_user_model
from jobs.models import Job
from applications.models import Application

User = get_user_model()


class FollowUpTemplate(models.Model):
    TRIGGER_TYPES = [
        ('application_received', 'Application Received'),
        ('application_viewed', 'Application Viewed'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('interview_completed', 'Interview Completed'),
        ('offer_extended', 'Offer Extended'),
        ('offer_accepted', 'Offer Accepted'),
        ('offer_declined', 'Offer Declined'),
        ('rejection_sent', 'Rejection Sent'),
        ('custom', 'Custom Trigger'),
    ]
    
    name = models.CharField(max_length=200)
    trigger_type = models.CharField(max_length=30, choices=TRIGGER_TYPES)
    subject = models.CharField(max_length=255)
    content = models.TextField()
    variables = models.JSONField(default=list)  # List of variable names
    delay_days = models.IntegerField(default=0, help_text="Days after trigger to send follow-up")
    delay_hours = models.IntegerField(default=0, help_text="Hours after trigger to send follow-up")
    is_active = models.BooleanField(default=True)
    is_one_time = models.BooleanField(default=False, help_text="Send only once per candidate")
    priority = models.IntegerField(default=5, help_text="Lower number = higher priority")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_followup_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['priority', 'name']

    def __str__(self):
        return f"{self.name} ({self.trigger_type})"


class FollowUpRule(models.Model):
    CONDITION_TYPES = [
        ('all', 'All Applications'),
        ('specific_job', 'Specific Job'),
        ('job_category', 'Job Category'),
        ('candidate_stage', 'Candidate Stage'),
        ('time_based', 'Time Based'),
        ('custom', 'Custom Condition'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    condition_type = models.CharField(max_length=20, choices=CONDITION_TYPES)
    conditions = models.JSONField(default=dict)  # Flexible condition storage
    templates = models.ManyToManyField(FollowUpTemplate, related_name='rules')
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    max_sends_per_candidate = models.IntegerField(default=1)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_followup_rules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class FollowUpSchedule(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('skipped', 'Skipped'),
    ]
    
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follow_up_schedules')
    application = models.ForeignKey(Application, on_delete=models.CASCADE, null=True, blank=True, related_name='follow_up_schedules')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True, related_name='follow_up_schedules')
    template = models.ForeignKey(FollowUpTemplate, on_delete=models.CASCADE, related_name='schedules')
    rule = models.ForeignKey(FollowUpRule, on_delete=models.CASCADE, null=True, blank=True, related_name='schedules')
    
    # Scheduling details
    scheduled_at = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    # Message details
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=255)
    content = models.TextField()
    variables_used = models.JSONField(default=dict)
    
    # Tracking
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)
    last_error = models.TextField(blank=True)
    
    # Response tracking
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['scheduled_at']
        indexes = [
            models.Index(fields=['status', 'scheduled_at']),
            models.Index(fields=['candidate', 'status']),
            models.Index(fields=['template', 'status']),
        ]

    def __str__(self):
        return f"{self.candidate.email} - {self.template.name} ({self.status})"


class FollowUpHistory(models.Model):
    ACTION_TYPES = [
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('opened', 'Opened'),
        ('clicked', 'Clicked'),
        ('replied', 'Replied'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('skipped', 'Skipped'),
    ]
    
    schedule = models.ForeignKey(FollowUpSchedule, on_delete=models.CASCADE, related_name='history')
    action_type = models.CharField(max_length=10, choices=ACTION_TYPES)
    action_date = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-action_date']

    def __str__(self):
        return f"{self.schedule.template.name} - {self.action_type}"


class FollowUpTrigger(models.Model):
    TRIGGER_EVENTS = [
        ('application_submitted', 'Application Submitted'),
        ('application_status_changed', 'Application Status Changed'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('interview_completed', 'Interview Completed'),
        ('offer_sent', 'Offer Sent'),
        ('offer_responded', 'Offer Responded'),
        ('candidate_hired', 'Candidate Hired'),
        ('candidate_rejected', 'Candidate Rejected'),
    ]
    
    event_type = models.CharField(max_length=30, choices=TRIGGER_EVENTS)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, null=True, blank=True, related_name='follow_up_triggers')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follow_up_triggers')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True, related_name='follow_up_triggers')
    
    # Event data
    event_data = models.JSONField(default=dict)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Processing results
    schedules_created = models.IntegerField(default=0)
    errors = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', 'processed']),
            models.Index(fields=['candidate', 'processed']),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.candidate.email}"


class FollowUpAnalytics(models.Model):
    date = models.DateField()
    template = models.ForeignKey(FollowUpTemplate, on_delete=models.CASCADE, null=True, blank=True, related_name='analytics')
    rule = models.ForeignKey(FollowUpRule, on_delete=models.CASCADE, null=True, blank=True, related_name='analytics')
    
    # Metrics
    total_scheduled = models.IntegerField(default=0)
    total_sent = models.IntegerField(default=0)
    total_failed = models.IntegerField(default=0)
    total_opened = models.IntegerField(default=0)
    total_clicked = models.IntegerField(default=0)
    total_replied = models.IntegerField(default=0)
    
    # Rates
    open_rate = models.FloatField(default=0.0)
    click_rate = models.FloatField(default=0.0)
    reply_rate = models.FloatField(default=0.0)
    success_rate = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['date', 'template', 'rule']
        ordering = ['-date']

    def __str__(self):
        return f"Analytics for {self.date} - {self.template.name if self.template else 'All'}"


class FollowUpBlacklist(models.Model):
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follow_up_blacklist')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True, related_name='follow_up_blacklist')
    template = models.ForeignKey(FollowUpTemplate, on_delete=models.CASCADE, null=True, blank=True, related_name='blacklist')
    rule = models.ForeignKey(FollowUpRule, on_delete=models.CASCADE, null=True, blank=True, related_name='blacklist')
    
    reason = models.CharField(max_length=255)
    is_permanent = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_blacklist_entries')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['candidate', 'job', 'template', 'rule']

    def __str__(self):
        return f"Blacklist: {self.candidate.email} - {self.reason}"
