from django.urls import path
from .views import (
    JobListCreateView,
    JobDetailView,
    RecruiterJobsView,
    RecruiterDashboardView,
)

urlpatterns = [
    path('', JobListCreateView.as_view()),
    path('<int:pk>/', JobDetailView.as_view()),

    # ── Recruiter-specific endpoints (Omar's) ──
    path('my-jobs/', RecruiterJobsView.as_view()),
    path('dashboard/', RecruiterDashboardView.as_view()),
]
