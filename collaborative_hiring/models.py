from django.db import models
from django.conf import settings
from django.utils import timezone
from jobs.models import Job
from applications.models import Application

User = settings.AUTH_USER_MODEL


class HiringTeam(models.Model):
    TEAM_TYPES = [
        ('recruiter', 'Recruiter Team'),
        ('hiring_manager', 'Hiring Manager'),
        ('interview_panel', 'Interview Panel'),
        ('stakeholder', 'Stakeholder'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    team_type = models.CharField(max_length=20, choices=TEAM_TYPES)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='hiring_teams')
    members = models.ManyToManyField(User, related_name='hiring_teams')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_hiring_teams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.team_type}"


class HiringDecision(models.Model):
    DECISION_CHOICES = [
        ('strong_yes', 'Strong Yes'),
        ('yes', 'Yes'),
        ('maybe', 'Maybe'),
        ('no', 'No'),
        ('strong_no', 'Strong No'),
    ]
    
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='hiring_decisions')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hiring_decisions_made')
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES)
    score = models.IntegerField(default=0)
    comments = models.TextField(blank=True)
    strengths = models.JSONField(default=list)
    concerns = models.JSONField(default=list)
    recommendation = models.TextField(blank=True)
    is_final = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.application} - {self.decision}"


class InterviewSchedule(models.Model):
    INTERVIEW_TYPES = [
        ('phone', 'Phone Interview'),
        ('video', 'Video Interview'),
        ('in_person', 'In-Person Interview'),
        ('panel', 'Panel Interview'),
        ('practical', 'Practical Test'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    scheduled_date = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    location = models.CharField(max_length=255, blank=True)
    meeting_url = models.URLField(blank=True)
    interviewers = models.ManyToManyField(User, related_name='interview_schedules')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='candidate_interviews')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    feedback = models.TextField(blank=True)
    rating = models.IntegerField(null=True, blank=True)
    would_hire = models.BooleanField(null=True, blank=True)
    internal_notes = models.TextField(blank=True)
    candidate_notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_interview_schedules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"{self.title} - {self.application}"


class CandidateFeedback(models.Model):
    FEEDBACK_TYPES = [
        ('technical', 'Technical Assessment'),
        ('cultural_fit', 'Cultural Fit'),
        ('communication', 'Communication'),
        ('leadership', 'Leadership'),
        ('overall', 'Overall'),
    ]
    
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='candidate_feedback')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback_given')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    score = models.IntegerField()
    max_score = models.IntegerField(default=10)
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    observations = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    hire_recommendation = models.BooleanField(null=True, blank=True)
    is_shared_with_candidate = models.BooleanField(default=False)
    is_shared_with_team = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.application} - {self.feedback_type}"


class HiringWorkflow(models.Model):
    WORKFLOW_TYPES = [
        ('standard', 'Standard'),
        ('expedited', 'Expedited'),
        ('executive', 'Executive'),
        ('custom', 'Custom'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    workflow_type = models.CharField(max_length=20, choices=WORKFLOW_TYPES)
    stages = models.JSONField(default=list)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_workflows')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class JobWorkflow(models.Model):
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name='workflow')
    workflow = models.ForeignKey(HiringWorkflow, on_delete=models.SET_NULL, null=True, blank=True)
    current_stage = models.CharField(max_length=100, blank=True)
    stage_history = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Workflow for {self.job.title}"


class TeamCollaboration(models.Model):
    COLLAB_TYPES = [
        ('discussion', 'Discussion'),
        ('decision_needed', 'Decision Needed'),
        ('feedback_request', 'Feedback Request'),
        ('alert', 'Alert'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='collaborations')
    collaboration_type = models.CharField(max_length=20, choices=COLLAB_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    attachments = models.JSONField(default=list)
    initiator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='initiated_collaborations')
    participants = models.ManyToManyField(User, related_name='collaborations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    resolution = models.TextField(blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_collaborations')
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class InterviewKit(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    job_category = models.CharField(max_length=100)
    questions = models.JSONField(default=list)
    evaluation_criteria = models.JSONField(default=list)
    scoring_rubric = models.JSONField(default=dict)
    time_allocations = models.JSONField(default=dict)
    resources = models.JSONField(default=list)
    templates = models.JSONField(default=list)
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_interview_kits')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class JobInterviewKit(models.Model):
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name='interview_kit')
    interview_kit = models.ForeignKey(InterviewKit, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interview Kit for {self.job.title}"


class HiringAnalytics(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='hiring_analytics')
    team = models.ForeignKey(HiringTeam, on_delete=models.SET_NULL, null=True, blank=True)
    workflow = models.ForeignKey(HiringWorkflow, on_delete=models.SET_NULL, null=True, blank=True)
    total_applications = models.IntegerField(default=0)
    screened_applications = models.IntegerField(default=0)
    interviewed_count = models.IntegerField(default=0)
    offers_extended = models.IntegerField(default=0)
    offers_accepted = models.IntegerField(default=0)
    average_time_to_hire = models.IntegerField(default=0)  # in days
    quality_of_hire = models.FloatField(default=0.0)
    cost_per_hire = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    hiring_velocity = models.FloatField(default=0.0)
    analytics_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Analytics for {self.job.title}"


class TeamNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('assignment', 'New Assignment'),
        ('decision_needed', 'Decision Needed'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('feedback_requested', 'Feedback Requested'),
        ('status_update', 'Status Update'),
        ('alert', 'Alert'),
    ]
    
    team = models.ForeignKey(HiringTeam, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    related_to = models.CharField(max_length=100, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
