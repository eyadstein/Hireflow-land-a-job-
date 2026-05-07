from django.urls import path
from .views import (
    ApplyView,
    MyApplicationsView,
    JobApplicationsView,
    UpdateStatusView,
    CompareCandidatesView,
)

urlpatterns = [
    path('apply/', ApplyView.as_view()),
    path('mine/', MyApplicationsView.as_view()),
    path('job/<int:job_id>/', JobApplicationsView.as_view()),
    path('<int:pk>/status/', UpdateStatusView.as_view()),

    # Candidate Comparison Tool
    path('compare/', CompareCandidatesView.as_view()),
]