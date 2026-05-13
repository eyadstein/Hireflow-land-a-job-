from django.db import models
from django.contrib.auth import get_user_model
from jobs.models import Job
from applications.models import Application

User = get_user_model()


class CandidateProfile(models.Model):
    CANDIDATE_STATUS = [
        ('new', 'New'),
        ('active', 'Active'),
        ('engaged', 'Engaged'),
        ('interviewing', 'Interviewing'),
        ('offered', 'Offered'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
        ('inactive', 'Inactive'),
    ]
    
    SOURCE_TYPES = [
        ('website', 'Website'),
        ('referral', 'Referral'),
        ('linkedin', 'LinkedIn'),
        ('job_board', 'Job Board'),
        ('recruiter', 'Recruiter'),
        ('event', 'Event'),
        ('cold_email', 'Cold Email'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='crm_profile')
    status = models.CharField(max_length=20, choices=CANDIDATE_STATUS, default='new')
    source = models.CharField(max_length=20, choices=SOURCE_TYPES, default='website')
    source_details = models.CharField(max_length=255, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_candidates')
    tags = models.JSONField(default=list)
    notes = models.TextField(blank=True)
    rating = models.IntegerField(default=0, help_text="1-5 rating")
    is_active = models.BooleanField(default=True)
    last_contacted = models.DateTimeField(null=True, blank=True)
    next_follow_up = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'assigned_to']),
            models.Index(fields=['source']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.status}"


class CandidateInteraction(models.Model):
    INTERACTION_TYPES = [
        ('email', 'Email'),
        ('phone', 'Phone Call'),
        ('meeting', 'Meeting'),
        ('interview', 'Interview'),
        ('note', 'Note'),
        ('task', 'Task'),
        ('application', 'Application'),
        ('offer', 'Offer'),
        ('rejection', 'Rejection'),
    ]
    
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    duration_minutes = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    attendees = models.JSONField(default=list)
    outcome = models.TextField(blank=True)
    next_steps = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_interactions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['candidate', 'date']),
            models.Index(fields=['interaction_type']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f"{self.candidate.user.email} - {self.interaction_type} - {self.date}"


class CandidateTask(models.Model):
    TASK_STATUS = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=TASK_STATUS, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    due_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='candidate_tasks')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_candidate_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', '-created_at']
        indexes = [
            models.Index(fields=['candidate', 'status']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['priority', 'due_date']),
        ]

    def __str__(self):
        return f"{self.candidate.user.email} - {self.title} ({self.status})"


class CandidateDocument(models.Model):
    DOCUMENT_TYPES = [
        ('resume', 'Resume'),
        ('cover_letter', 'Cover Letter'),
        ('portfolio', 'Portfolio'),
        ('transcript', 'Transcript'),
        ('certificate', 'Certificate'),
        ('contract', 'Contract'),
        ('offer_letter', 'Offer Letter'),
        ('nda', 'NDA'),
        ('other', 'Other'),
    ]
    
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='candidate_documents/')
    file_size = models.IntegerField(null=True, blank=True)
    file_type = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_documents')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['candidate', 'document_type']),
            models.Index(fields=['uploaded_by']),
        ]

    def __str__(self):
        return f"{self.candidate.user.email} - {self.title}"


class CandidatePipeline(models.Model):
    PIPELINE_STAGES = [
        ('sourcing', 'Sourcing'),
        ('screening', 'Screening'),
        ('interview', 'Interview'),
        ('assessment', 'Assessment'),
        ('reference_check', 'Reference Check'),
        ('offer', 'Offer'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    stages = models.JSONField(default=list)  # Custom stages configuration
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_pipelines')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CandidatePipelineStage(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='pipeline_stages')
    pipeline = models.ForeignKey(CandidatePipeline, on_delete=models.CASCADE, related_name='candidate_stages')
    stage = models.CharField(max_length=50)
    stage_order = models.IntegerField(default=0)
    entered_at = models.DateTimeField(auto_now_add=True)
    exited_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    moved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moved_candidates')

    class Meta:
        ordering = ['pipeline', 'stage_order', 'entered_at']
        unique_together = ['candidate', 'pipeline']
        indexes = [
            models.Index(fields=['pipeline', 'stage']),
            models.Index(fields=['candidate', 'entered_at']),
        ]

    def __str__(self):
        return f"{self.candidate.user.email} - {self.pipeline.name} - {self.stage}"


class CandidateTag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tags')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CandidateEmail(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='emails')
    subject = models.CharField(max_length=255)
    content = models.TextField()
    direction = models.CharField(max_length=10, choices=[('inbound', 'Inbound'), ('outbound', 'Outbound')])
    sent_at = models.DateTimeField()
    received_at = models.DateTimeField(null=True, blank=True)
    sender_email = models.EmailField()
    recipient_email = models.EmailField()
    is_read = models.BooleanField(default=False)
    thread_id = models.CharField(max_length=255, blank=True)
    attachments = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['candidate', 'sent_at']),
            models.Index(fields=['direction']),
            models.Index(fields=['thread_id']),
        ]

    def __str__(self):
        return f"{self.candidate.user.email} - {self.subject}"


class CandidateActivity(models.Model):
    ACTIVITY_TYPES = [
        ('profile_view', 'Profile View'),
        ('document_download', 'Document Download'),
        ('email_sent', 'Email Sent'),
        ('email_received', 'Email Received'),
        ('task_completed', 'Task Completed'),
        ('status_change', 'Status Change'),
        ('note_added', 'Note Added'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('offer_made', 'Offer Made'),
    ]
    
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    details = models.JSONField(default=dict)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='candidate_activities')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['candidate', 'created_at']),
            models.Index(fields=['activity_type']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.candidate.user.email} - {self.activity_type}"


class CandidateRelationship(models.Model):
    RELATIONSHIP_TYPES = [
        ('referral', 'Referral'),
        ('colleague', 'Colleague'),
        ('manager', 'Manager'),
        ('mentor', 'Mentor'),
        ('friend', 'Friend'),
        ('family', 'Family'),
        ('client', 'Client'),
        ('vendor', 'Vendor'),
    ]
    
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='relationships')
    related_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='candidate_relationships')
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_TYPES)
    company = models.CharField(max_length=255, blank=True)
    position = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_relationships')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['candidate', 'related_user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.candidate.user.email} - {self.related_user.email} ({self.relationship_type})"
