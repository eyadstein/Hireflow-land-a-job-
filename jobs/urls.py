from django.urls import path
from .views import (
    JobListCreateView,
    JobDetailView,
    SavedJobListView,
    SaveJobView,
    CheckSavedJobView,
    SavedJobNotesView,
    SavedJobStatsView,
    JobAlertListCreateView,
    JobAlertDetailView,
    JobAlertToggleView,
    CheckAlertsView,
    AlertMatchesView,
)

urlpatterns = [
    # Internal jobs
    path('', JobListCreateView.as_view()),
    path('<int:pk>/', JobDetailView.as_view()),

    # Saved jobs
    path('saved/', SavedJobListView.as_view()),
    path('saved/toggle/', SaveJobView.as_view()),
    path('saved/stats/', SavedJobStatsView.as_view()),
    path('saved/check/<str:job_id>/', CheckSavedJobView.as_view()),
    path('saved/notes/<str:job_id>/', SavedJobNotesView.as_view()),

    # Job alerts
    path('alerts/', JobAlertListCreateView.as_view()),
    path('alerts/<int:pk>/', JobAlertDetailView.as_view()),
    path('alerts/<int:pk>/toggle/', JobAlertToggleView.as_view()),
    path('alerts/check/', CheckAlertsView.as_view()),
    path('alerts/matches/', AlertMatchesView.as_view()),
]