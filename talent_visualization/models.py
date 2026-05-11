from django.db import models
from django.contrib.auth import get_user_model
from jobs.models import Job
from applications.models import Application

User = get_user_model()


class TalentPool(models.Model):
    POOL_TYPES = [
        ('active', 'Active Candidates'),
        ('passive', 'Passive Candidates'),
        ('alumni', 'Alumni Network'),
        ('referrals', 'Referral Network'),
        ('sourced', 'Sourced Candidates'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    pool_type = models.CharField(max_length=20, choices=POOL_TYPES)
    job_category = models.CharField(max_length=100, blank=True)
    skills = models.JSONField(default=list)
    experience_levels = models.JSONField(default=list)
    locations = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_talent_pools')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class TalentPoolCandidate(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('contacted', 'Contacted'),
        ('screening', 'Screening'),
        ('interviewing', 'Interviewing'),
        ('offered', 'Offered'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    talent_pool = models.ForeignKey(TalentPool, on_delete=models.CASCADE, related_name='candidates')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='talent_pool_memberships')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    skills = models.JSONField(default=list)
    experience_years = models.IntegerField(null=True, blank=True)
    education_level = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    salary_expectation = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    availability = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    last_contacted = models.DateTimeField(null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-added_at']
        unique_together = ['talent_pool', 'candidate']

    def __str__(self):
        return f"{self.candidate.get_full_name()} - {self.talent_pool.name}"


class TalentVisualization(models.Model):
    CHART_TYPES = [
        ('funnel', 'Hiring Funnel'),
        ('pipeline', 'Pipeline Status'),
        ('source_effectiveness', 'Source Effectiveness'),
        ('time_metrics', 'Time Metrics'),
        ('skill_distribution', 'Skill Distribution'),
        ('location_distribution', 'Location Distribution'),
        ('salary_analysis', 'Salary Analysis'),
        ('diversity_metrics', 'Diversity Metrics'),
        ('performance_trends', 'Performance Trends'),
    ]
    
    name = models.CharField(max_length=200)
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES)
    description = models.TextField(blank=True)
    configuration = models.JSONField(default=dict)
    data = models.JSONField(default=dict)
    filters = models.JSONField(default=dict)
    is_public = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_visualizations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class TalentAnalytics(models.Model):
    METRIC_TYPES = [
        ('pool_size', 'Pool Size'),
        ('pipeline_velocity', 'Pipeline Velocity'),
        ('time_to_hire', 'Time to Hire'),
        ('offer_acceptance_rate', 'Offer Acceptance Rate'),
        ('source_quality', 'Source Quality'),
        ('skill_gap_analysis', 'Skill Gap Analysis'),
        ('diversity_metrics', 'Diversity Metrics'),
        ('cost_per_hire', 'Cost Per Hire'),
        ('candidate_satisfaction', 'Candidate Satisfaction'),
    ]
    
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPES)
    value = models.FloatField(default=0.0)
    metadata = models.JSONField(default=dict)
    date = models.DateField()
    
    # Context
    talent_pool = models.ForeignKey(TalentPool, on_delete=models.CASCADE, null=True, blank=True, related_name='analytics')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True, related_name='analytics')
    visualization = models.ForeignKey(TalentVisualization, on_delete=models.CASCADE, null=True, blank=True, related_name='analytics')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['metric_type', 'date', 'talent_pool', 'job', 'visualization']

    def __str__(self):
        return f"{self.metric_type} - {self.date}: {self.value}"


class TalentDashboard(models.Model):
    DASHBOARD_TYPES = [
        ('executive', 'Executive Dashboard'),
        ('recruiter', 'Recruiter Dashboard'),
        ('hiring_manager', 'Hiring Manager Dashboard'),
        ('interviewer', 'Interviewer Dashboard'),
        ('analytics', 'Analytics Dashboard'),
    ]
    
    name = models.CharField(max_length=200)
    dashboard_type = models.CharField(max_length=20, choices=DASHBOARD_TYPES)
    description = models.TextField(blank=True)
    layout = models.JSONField(default=dict)
    widgets = models.JSONField(default=list)
    filters = models.JSONField(default=dict)
    refresh_interval = models.IntegerField(default=300)  # seconds
    is_public = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_dashboards')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class UserDashboard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_dashboards')
    dashboard = models.ForeignKey(TalentDashboard, on_delete=models.CASCADE, related_name='user_dashboards')
    is_favorite = models.BooleanField(default=False)
    custom_filters = models.JSONField(default=dict)
    custom_layout = models.JSONField(default=dict)
    last_accessed = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-last_accessed']
        unique_together = ['user', 'dashboard']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.dashboard.name}"


class TalentReport(models.Model):
    REPORT_TYPES = [
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('quarterly', 'Quarterly Report'),
        ('annual', 'Annual Report'),
        ('custom', 'Custom Report'),
    ]
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    template = models.JSONField(default=dict)
    data = models.JSONField(default=dict)
    filters = models.JSONField(default=dict)
    format = models.CharField(max_length=20, default='pdf')
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=20, blank=True)
    last_generated = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ReportSchedule(models.Model):
    report = models.ForeignKey(TalentReport, on_delete=models.CASCADE, related_name='schedules')
    recipients = models.ManyToManyField(User, related_name='report_schedules')
    frequency = models.CharField(max_length=20)
    next_run = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_report_schedules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['next_run']

    def __str__(self):
        return f"{self.report.name} - {self.frequency}"


class TalentInsight(models.Model):
    INSIGHT_TYPES = [
        ('trend', 'Trend Analysis'),
        ('anomaly', 'Anomaly Detection'),
        ('prediction', 'Predictive Analysis'),
        ('correlation', 'Correlation Analysis'),
        ('benchmark', 'Benchmark Comparison'),
        ('recommendation', 'Recommendation Engine'),
    ]
    
    title = models.CharField(max_length=200)
    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPES)
    description = models.TextField()
    data_points = models.JSONField(default=list)
    confidence_score = models.FloatField(default=0.0)
    impact_level = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        default='medium'
    )
    action_items = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_insights')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
