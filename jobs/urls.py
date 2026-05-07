from django.urls import path
from .views import (
    JobListCreateView,
    JobDetailView,
    PerformanceSummaryView,
    ActivityLogView,
    DecisionPatternsView,
    BusiestPeriodsView,
    ResponseTimesView,
)

urlpatterns = [
    path('', JobListCreateView.as_view()),
    path('<int:pk>/', JobDetailView.as_view()),

    # Recruiter Performance Analytics
    path('performance/summary/', PerformanceSummaryView.as_view()),
    path('performance/activity-log/', ActivityLogView.as_view()),
    path('performance/decision-patterns/', DecisionPatternsView.as_view()),
    path('performance/busiest-periods/', BusiestPeriodsView.as_view()),
    path('performance/response-times/', ResponseTimesView.as_view()),
]