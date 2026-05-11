from django.db import models
from django.contrib.auth import get_user_model
from jobs.models import Job

User = get_user_model()


class TalentPool(models.Model):
    POOL_TYPES = [
        ('active', 'Active Candidates'),
        ('passive', 'Passive Candidates'),
        ('alumni', 'Alumni'),
        ('referrals', 'Referrals'),
        ('diversity', 'Diversity Pool'),
        ('interns', 'Intern Pool'),
        ('executives', 'Executive Pool'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    pool_type = models.CharField(max_length=20, choices=POOL_TYPES)
    criteria = models.JSONField(default=dict)  # Pool criteria
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_talent_pools')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.pool_type})"


class TalentCandidate(models.Model):
    SOURCE_TYPES = [
        ('linkedin', 'LinkedIn'),
        ('github', 'GitHub'),
        ('stackoverflow', 'Stack Overflow'),
        ('twitter', 'Twitter'),
        ('personal_website', 'Personal Website'),
        ('portfolio', 'Portfolio'),
        ('referral', 'Referral'),
        ('event', 'Event'),
        ('database', 'Database'),
        ('other', 'Other'),
    ]
    
    pool = models.ForeignKey(TalentPool, on_delete=models.CASCADE, related_name='candidates')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='talent_profiles')
    
    # Profile information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Professional information
    title = models.CharField(max_length=200, blank=True)
    company = models.CharField(max_length=200, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    experience_years = models.FloatField(default=0)
    skills = models.JSONField(default=list)
    education = models.JSONField(default=list)
    
    # Online presence
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    personal_website = models.URLField(blank=True)
    
    # Discovery details
    source = models.CharField(max_length=20, choices=SOURCE_TYPES)
    source_details = models.TextField(blank=True)
    discovered_at = models.DateTimeField(auto_now_add=True)
    last_contacted = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, default='new')
    is_active = models.BooleanField(default=True)
    is_interested = models.BooleanField(default=False)
    response_rate = models.FloatField(default=0.0)
    
    # Notes
    notes = models.TextField(blank=True)
    tags = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-discovered_at']
        indexes = [
            models.Index(fields=['pool', 'status']),
            models.Index(fields=['skills']),
            models.Index(fields=['location']),
            models.Index(fields=['industry']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.pool.name}"


class TalentSearch(models.Model):
    SEARCH_TYPES = [
        ('keyword', 'Keyword Search'),
        ('skill', 'Skill Search'),
        ('location', 'Location Search'),
        ('company', 'Company Search'),
        ('industry', 'Industry Search'),
        ('ai_powered', 'AI Powered Search'),
        ('boolean', 'Boolean Search'),
    ]
    
    name = models.CharField(max_length=200)
    search_type = models.CharField(max_length=20, choices=SEARCH_TYPES)
    query = models.JSONField(default=dict)  # Search parameters
    filters = models.JSONField(default=dict)  # Additional filters
    results_count = models.IntegerField(default=0)
    is_saved = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='talent_searches')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.search_type}"


class TalentEngagement(models.Model):
    ENGAGEMENT_TYPES = [
        ('email', 'Email'),
        ('phone', 'Phone Call'),
        ('linkedin', 'LinkedIn Message'),
        ('sms', 'SMS'),
        ('inmail', 'LinkedIn InMail'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('opened', 'Opened'),
        ('replied', 'Replied'),
        ('interested', 'Interested'),
        ('not_interested', 'Not Interested'),
        ('bounced', 'Bounced'),
        ('failed', 'Failed'),
    ]
    
    candidate = models.ForeignKey(TalentCandidate, on_delete=models.CASCADE, related_name='engagements')
    engagement_type = models.CharField(max_length=20, choices=ENGAGEMENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    
    # Message details
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    template_used = models.CharField(max_length=100, blank=True)
    
    # Tracking
    sent_at = models.DateTimeField(auto_now_add=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    
    # Response
    response = models.TextField(blank=True)
    next_action = models.TextField(blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='talent_engagements')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['candidate', 'status']),
            models.Index(fields=['engagement_type']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f"{self.candidate.first_name} {self.candidate.last_name} - {self.engagement_type}"


class TalentCampaign(models.Model):
    CAMPAIGN_TYPES = [
        ('email', 'Email Campaign'),
        ('linkedin', 'LinkedIn Campaign'),
        ('multi_channel', 'Multi-Channel Campaign'),
        ('nurturing', 'Nurturing Campaign'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Targeting
    target_pools = models.ManyToManyField(TalentPool, related_name='campaigns')
    target_criteria = models.JSONField(default=dict)
    
    # Content
    subject = models.CharField(max_length=255, blank=True)
    message_template = models.TextField()
    personalization_vars = models.JSONField(default=dict)
    
    # Schedule
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    send_immediately = models.BooleanField(default=False)
    
    # Results
    total_sent = models.IntegerField(default=0)
    total_opened = models.IntegerField(default=0)
    total_replied = models.IntegerField(default=0)
    total_interested = models.IntegerField(default=0)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='talent_campaigns')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.status})"


class TalentCampaignExecution(models.Model):
    campaign = models.ForeignKey(TalentCampaign, on_delete=models.CASCADE, related_name='executions')
    candidate = models.ForeignKey(TalentCandidate, on_delete=models.CASCADE, related_name='campaign_executions')
    
    # Execution details
    sent_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='pending')
    
    # Personalized content
    personalized_subject = models.CharField(max_length=255, blank=True)
    personalized_message = models.TextField(blank=True)
    
    # Results
    opened_at = models.DateTimeField(null=True, blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    response = models.TextField(blank=True)
    
    # Tracking
    tracking_id = models.CharField(max_length=100, unique=True)
    opened_count = models.IntegerField(default=0)
    clicked_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['campaign', 'candidate']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.campaign.name} - {self.candidate.first_name} {self.candidate.last_name}"


class TalentInsight(models.Model):
    INSIGHT_TYPES = [
        ('skill_trend', 'Skill Trend'),
        ('location_demand', 'Location Demand'),
        ('salary_insight', 'Salary Insight'),
        ('competition_analysis', 'Competition Analysis'),
        ('market_gap', 'Market Gap'),
        ('diversity_metric', 'Diversity Metric'),
    ]
    
    insight_type = models.CharField(max_length=30, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    data = models.JSONField(default=dict)
    confidence_score = models.FloatField(default=0.0)
    
    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    source = models.CharField(max_length=100, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['insight_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['generated_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.insight_type})"


class TalentSource(models.Model):
    SOURCE_TYPES = [
        ('linkedin', 'LinkedIn'),
        ('github', 'GitHub'),
        ('stackoverflow', 'Stack Overflow'),
        ('indeed', 'Indeed'),
        ('glassdoor', 'Glassdoor'),
        ('angellist', 'AngelList'),
        ('hired', 'Hired'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    base_url = models.URLField()
    api_endpoint = models.URLField(blank=True)
    
    # Authentication
    api_key = models.CharField(max_length=255, blank=True)
    api_secret = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Rate limiting
    requests_per_hour = models.IntegerField(default=100)
    requests_per_day = models.IntegerField(default=1000)
    
    # Configuration
    search_config = models.JSONField(default=dict)
    field_mapping = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.source_type})"


class TalentSourcingRule(models.Model):
    RULE_TYPES = [
        ('keyword', 'Keyword Based'),
        ('skill', 'Skill Based'),
        ('location', 'Location Based'),
        ('experience', 'Experience Based'),
        ('company', 'Company Based'),
        ('ai_model', 'AI Model'),
    ]
    
    name = models.CharField(max_length=200)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES)
    conditions = models.JSONField(default=dict)
    actions = models.JSONField(default=dict)
    
    # Execution
    is_active = models.BooleanField(default=True)
    run_frequency = models.CharField(max_length=20, default='daily')
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    
    # Results
    candidates_found = models.IntegerField(default=0)
    candidates_added = models.IntegerField(default=0)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sourcing_rules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.rule_type})"


class TalentAnalytics(models.Model):
    METRIC_TYPES = [
        ('pool_size', 'Pool Size'),
        ('engagement_rate', 'Engagement Rate'),
        ('response_rate', 'Response Rate'),
        ('conversion_rate', 'Conversion Rate'),
        ('time_to_hire', 'Time to Hire'),
        ('cost_per_hire', 'Cost per Hire'),
        ('source_effectiveness', 'Source Effectiveness'),
    ]
    
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPES)
    date = models.DateField()
    value = models.FloatField(default=0.0)
    metadata = models.JSONField(default=dict)
    
    # Context
    pool = models.ForeignKey(TalentPool, on_delete=models.CASCADE, null=True, blank=True, related_name='analytics')
    campaign = models.ForeignKey(TalentCampaign, on_delete=models.CASCADE, null=True, blank=True, related_name='analytics')
    source = models.ForeignKey(TalentSource, on_delete=models.CASCADE, null=True, blank=True, related_name='analytics')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['metric_type', 'date', 'pool', 'campaign', 'source']
        ordering = ['-date']

    def __str__(self):
        return f"{self.metric_type} - {self.date}: {self.value}"
