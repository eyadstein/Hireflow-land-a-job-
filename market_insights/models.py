from django.db import models
from django.contrib.auth import get_user_model
from jobs.models import Job

User = get_user_model()


class MarketData(models.Model):
    DATA_TYPES = [
        ('salary', 'Salary Data'),
        ('demand', 'Demand Data'),
        ('skills', 'Skills Data'),
        ('location', 'Location Data'),
        ('industry', 'Industry Data'),
        ('experience', 'Experience Data'),
    ]
    
    data_type = models.CharField(max_length=20, choices=DATA_TYPES)
    job_category = models.CharField(max_length=100)
    job_title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    industry = models.CharField(max_length=100, blank=True)
    experience_level = models.CharField(max_length=50, blank=True)
    data_value = models.JSONField(default=dict)
    source = models.CharField(max_length=100, blank=True)
    collection_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-collection_date']
        unique_together = ['data_type', 'job_category', 'job_title', 'location', 'collection_date']

    def __str__(self):
        return f"{self.job_title} - {self.location} ({self.data_type})"


class SalaryInsight(models.Model):
    INSIGHT_TYPES = [
        ('market_rate', 'Market Rate'),
        ('salary_range', 'Salary Range'),
        ('percentile', 'Percentile Analysis'),
        ('trend', 'Salary Trend'),
        ('comparison', 'Salary Comparison'),
        ('regional', 'Regional Analysis'),
    ]
    
    job_title = models.CharField(max_length=200)
    job_category = models.CharField(max_length=100)
    experience_level = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=200)
    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPES)
    salary_data = models.JSONField(default=dict)
    min_salary = models.DecimalField(max_digits=10, decimal_places=2)
    max_salary = models.DecimalField(max_digits=10, decimal_places=2)
    median_salary = models.DecimalField(max_digits=10, decimal_places=2)
    mean_salary = models.DecimalField(max_digits=10, decimal_places=2)
    percentile_25 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    percentile_75 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    data_points = models.IntegerField(default=0)
    confidence_level = models.FloatField(default=0.95)
    last_updated = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_salary_insights')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_updated']
        unique_together = ['job_title', 'job_category', 'experience_level', 'location', 'insight_type']

    def __str__(self):
        return f"{self.job_title} - {self.location} ({self.insight_type})"


class DemandAnalysis(models.Model):
    DEMAND_LEVELS = [
        ('low', 'Low Demand'),
        ('medium', 'Medium Demand'),
        ('high', 'High Demand'),
        ('very_high', 'Very High Demand'),
    ]
    
    job_category = models.CharField(max_length=100)
    job_title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    demand_level = models.CharField(max_length=20, choices=DEMAND_LEVELS)
    demand_score = models.FloatField(default=0.0)
    job_postings = models.IntegerField(default=0)
    active_candidates = models.IntegerField(default=0)
    hiring_velocity = models.FloatField(default=0.0)
    time_to_fill = models.IntegerField(default=0)  # days
    growth_rate = models.FloatField(default=0.0)  # percentage
    competition_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low Competition'),
            ('medium', 'Medium Competition'),
            ('high', 'High Competition'),
        ],
        default='medium'
    )
    analysis_date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_demand_analyses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-analysis_date']
        unique_together = ['job_title', 'location', 'analysis_date']

    def __str__(self):
        return f"{self.job_title} - {self.location} ({self.demand_level})"


class SkillsAnalysis(models.Model):
    SKILL_TYPES = [
        ('technical', 'Technical Skills'),
        ('soft', 'Soft Skills'),
        ('certification', 'Certifications'),
        ('language', 'Languages'),
        ('tool', 'Tools/Software'),
    ]
    
    skill_name = models.CharField(max_length=100)
    skill_type = models.CharField(max_length=20, choices=SKILL_TYPES)
    job_categories = models.JSONField(default=list)
    demand_level = models.CharField(
        max_length=20,
        choices=DemandAnalysis.DEMAND_LEVELS,
        default='medium'
    )
    growth_trend = models.CharField(
        max_length=20,
        choices=[
            ('declining', 'Declining'),
            ('stable', 'Stable'),
            ('growing', 'Growing'),
            ('rapidly_growing', 'Rapidly Growing'),
        ],
        default='stable'
    )
    salary_impact = models.FloatField(default=0.0)  # percentage impact on salary
    market_saturation = models.FloatField(default=0.0)  # percentage of candidates with this skill
    learning_time = models.IntegerField(default=0)  # months to learn
    analysis_date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_skills_analyses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-analysis_date']
        unique_together = ['skill_name', 'analysis_date']

    def __str__(self):
        return f"{self.skill_name} ({self.skill_type})"


class MarketTrend(models.Model):
    TREND_TYPES = [
        ('salary', 'Salary Trend'),
        ('demand', 'Demand Trend'),
        ('skills', 'Skills Trend'),
        ('location', 'Location Trend'),
        ('industry', 'Industry Trend'),
    ]
    
    trend_type = models.CharField(max_length=20, choices=TREND_TYPES)
    category = models.CharField(max_length=100)  # job category, skill, location, etc.
    title = models.CharField(max_length=200)
    trend_data = models.JSONField(default=dict)  # time series data
    trend_direction = models.CharField(
        max_length=20,
        choices=[
            ('decreasing', 'Decreasing'),
            ('stable', 'Stable'),
            ('increasing', 'Increasing'),
            ('volatile', 'Volatile'),
        ],
        default='stable'
    )
    change_percentage = models.FloatField(default=0.0)
    confidence_interval = models.JSONField(default=dict)
    prediction_period = models.IntegerField(default=12)  # months
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_market_trends')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['trend_type', 'category', 'title']

    def __str__(self):
        return f"{self.title} - {self.trend_type}"


class CompensationBenchmark(models.Model):
    BENCHMARK_TYPES = [
        ('industry', 'Industry Benchmark'),
        ('company_size', 'Company Size Benchmark'),
        ('location', 'Location Benchmark'),
        ('experience', 'Experience Benchmark'),
        ('role', 'Role Benchmark'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='compensation_benchmarks')
    benchmark_type = models.CharField(max_length=20, choices=BENCHMARK_TYPES)
    benchmark_category = models.CharField(max_length=100)
    base_salary_min = models.DecimalField(max_digits=10, decimal_places=2)
    base_salary_max = models.DecimalField(max_digits=10, decimal_places=2)
    base_salary_median = models.DecimalField(max_digits=10, decimal_places=2)
    total_comp_min = models.DecimalField(max_digits=10, decimal_places=2)
    total_comp_max = models.DecimalField(max_digits=10, decimal_places=2)
    total_comp_median = models.DecimalField(max_digits=10, decimal_places=2)
    bonus_percentage = models.FloatField(default=0.0)
    equity_range = models.JSONField(default=dict)
    benefits_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    currency = models.CharField(max_length=3, default='USD')
    sample_size = models.IntegerField(default=0)
    data_quality_score = models.FloatField(default=0.0)
    last_updated = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_benchmarks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_updated']
        unique_together = ['job', 'benchmark_type', 'benchmark_category']

    def __str__(self):
        return f"{self.job.title} - {self.benchmark_type}"


class MarketReport(models.Model):
    REPORT_TYPES = [
        ('salary', 'Salary Report'),
        ('demand', 'Demand Report'),
        ('skills', 'Skills Report'),
        ('trends', 'Trends Report'),
        ('comprehensive', 'Comprehensive Report'),
    ]
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    parameters = models.JSONField(default=dict)  # filters, criteria, etc.
    data = models.JSONField(default=dict)
    insights = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    format = models.CharField(
        max_length=20,
        choices=[
            ('pdf', 'PDF'),
            ('excel', 'Excel'),
            ('json', 'JSON'),
            ('html', 'HTML'),
        ],
        default='pdf'
    )
    is_public = models.BooleanField(default=False)
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=20, blank=True)
    last_generated = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_market_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ReportSubscription(models.Model):
    report = models.ForeignKey(MarketReport, on_delete=models.CASCADE, related_name='subscriptions')
    subscribers = models.ManyToManyField(User, related_name='market_report_subscriptions')
    frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
        ],
        default='monthly'
    )
    next_delivery = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_report_subscriptions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['next_delivery']
        unique_together = ['report', 'frequency']

    def __str__(self):
        return f"{self.report.name} - {self.frequency}"


class MarketAlert(models.Model):
    ALERT_TYPES = [
        ('salary_change', 'Salary Change'),
        ('demand_spike', 'Demand Spike'),
        ('skill_trend', 'Skill Trend'),
        ('market_shift', 'Market Shift'),
        ('competition', 'Competition Alert'),
    ]
    
    title = models.CharField(max_length=200)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    description = models.TextField()
    severity = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        default='medium'
    )
    affected_roles = models.JSONField(default=list)
    affected_locations = models.JSONField(default=list)
    trigger_conditions = models.JSONField(default=dict)
    action_required = models.BooleanField(default=False)
    action_items = models.JSONField(default=list)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_market_alerts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
