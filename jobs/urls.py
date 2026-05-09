from django.urls import path
from .views import (
    JobListCreateView,
    JobDetailView,
    RecruiterJobsView,
    RecruiterDashboardView,
    ApplicationTrendsView,
    JobTypeDistributionView,
    TopPerformingJobsView,
    StatusBreakdownView,
    HiringVelocityView,
    PerformanceSummaryView,
    ActivityLogView,
    DecisionPatternsView,
    BusiestPeriodsView,
    ResponseTimesView,
)

urlpatterns = [
    path('', JobListCreateView.as_view()),
    path('<int:pk>/', JobDetailView.as_view()),

    # Recruiter portal
    path('my-jobs/', RecruiterJobsView.as_view()),
    path('dashboard/', RecruiterDashboardView.as_view()),

    # Hiring Intelligence & Insights
    path('analytics/trends/', ApplicationTrendsView.as_view()),
    path('analytics/job-type-distribution/', JobTypeDistributionView.as_view()),
    path('analytics/top-jobs/', TopPerformingJobsView.as_view()),
    path('analytics/status-breakdown/', StatusBreakdownView.as_view()),
    path('analytics/hiring-velocity/', HiringVelocityView.as_view()),

    # Recruiter Performance Analytics
    path('performance/summary/', PerformanceSummaryView.as_view()),
    path('performance/activity-log/', ActivityLogView.as_view()),
    path('performance/decision-patterns/', DecisionPatternsView.as_view()),
    path('performance/busiest-periods/', BusiestPeriodsView.as_view()),
    path('performance/response-times/', ResponseTimesView.as_view()),
]
