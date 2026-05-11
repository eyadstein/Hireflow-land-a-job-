from django.db import models
from django.contrib.auth import get_user_model
from jobs.models import Job

User = get_user_model()


class Message(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('file', 'File'),
        ('image', 'Image'),
        ('voice', 'Voice'),
        ('video', 'Video'),
        ('system', 'System'),
    ]
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    attachment_url = models.URLField(blank=True)
    attachment_name = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True, related_name='messages')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender', 'recipient']),
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.sender.email} → {self.recipient.email}: {self.subject[:50]}"


class MessageThread(models.Model):
    participants = models.ManyToManyField(User, related_name='message_threads')
    subject = models.CharField(max_length=255)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True, related_name='threads')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_threads')
    last_message_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-last_message_at']

    def __str__(self):
        return f"Thread: {self.subject} ({self.participants.count()} participants)"


class ThreadMessage(models.Model):
    thread = models.ForeignKey(MessageThread, on_delete=models.CASCADE, related_name='thread_messages')
    message = models.OneToOneField(Message, on_delete=models.CASCADE, related_name='thread_message')
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ManyToManyField(User, blank=True, related_name='deleted_thread_messages')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('job_application', 'Job Application'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('offer_received', 'Offer Received'),
        ('profile_viewed', 'Profile Viewed'),
        ('message_received', 'Message Received'),
        ('job_match', 'Job Match'),
        ('system_update', 'System Update'),
        ('deadline_reminder', 'Deadline Reminder'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    is_email_sent = models.BooleanField(default=False)
    is_push_sent = models.BooleanField(default=False)
    action_url = models.URLField(blank=True)
    action_text = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.email}: {self.title}"


class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    message_notifications = models.BooleanField(default=True)
    job_match_notifications = models.BooleanField(default=True)
    application_notifications = models.BooleanField(default=True)
    interview_notifications = models.BooleanField(default=True)
    profile_view_notifications = models.BooleanField(default=True)
    system_notifications = models.BooleanField(default=True)
    daily_digest = models.BooleanField(default=False)
    weekly_digest = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - Preferences"


class MessageTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=255)
    content = models.TextField()
    variables = models.JSONField(default=list)  # List of variable names
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CommunicationLog(models.Model):
    ACTION_TYPES = [
        ('sent', 'Sent'),
        ('received', 'Received'),
        ('read', 'Read'),
        ('deleted', 'Deleted'),
        ('archived', 'Archived'),
        ('forwarded', 'Forwarded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='communication_logs')
    action_type = models.CharField(max_length=10, choices=ACTION_TYPES)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True, related_name='logs')
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, null=True, blank=True, related_name='logs')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.email}: {self.action_type} at {self.created_at}"
