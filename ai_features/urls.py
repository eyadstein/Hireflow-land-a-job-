from django.urls import path
from .views import (
    ResumeAnalyzerView,
    CoverLetterView,
    SalaryEstimatorView,
    InterviewCoachView,
    AgentChatView,
    CareerRoadmapView,
    CareerRoadmapDetailView,
)

urlpatterns = [
    # ── Existing AI features ──────────────────────────────────────
    path('resume-analyzer/',  ResumeAnalyzerView.as_view()),
    path('cover-letter/',     CoverLetterView.as_view()),
    path('salary-estimator/', SalaryEstimatorView.as_view()),
    path('interview-coach/',  InterviewCoachView.as_view()),
    path('chat/',             AgentChatView.as_view()),

    # ── Step 7 — Career Roadmap ───────────────────────────────────
    path('career-roadmap/',        CareerRoadmapView.as_view()),
    path('career-roadmap/<int:pk>/', CareerRoadmapDetailView.as_view()),
]