from django.urls import path
from .views import (
    JobListCreateView,
    JobDetailView,
    SeekerStatsView,
    RecruiterStatsView,
)

urlpatterns = [
    # ── Jobs CRUD ─────────────────────────────────────────────────
    path('',         JobListCreateView.as_view()),
    path('<int:pk>/', JobDetailView.as_view()),

    # ── Analytics ─────────────────────────────────────────────────
    path('analytics/my-stats/',        SeekerStatsView.as_view()),
    path('analytics/recruiter-stats/', RecruiterStatsView.as_view()),
]