from django.urls import path
from .views import (
    ResumeAnalyzerView,
    CoverLetterView,
    SalaryEstimatorView,
    InterviewCoachView,
    AgentChatView,
    CareerRoadmapView,
    CareerRoadmapDetailView,
    CVBuilderView,
    CVDownloadView,
    MockInterviewStartView,
    MockInterviewSubmitView,
    MockInterviewHistoryView,
    MockInterviewDetailView,
    LinkedInOptimizerView,
    LinkedInOptimizerDetailView,
    CareerPathPredictorView,
    SkillGapAnalyzerView,
    MarketTrendsView,
    ResumeJobGapView,
    CompetitorAnalysisView,
    CareerIntelligenceHistoryView,
)

urlpatterns = [
    path('resume-analyzer/',     ResumeAnalyzerView.as_view()),
    path('cover-letter/',        CoverLetterView.as_view()),
    path('salary-estimator/',    SalaryEstimatorView.as_view()),
    path('interview-coach/',     InterviewCoachView.as_view()),
    path('chat/',                AgentChatView.as_view()),

    path('career-roadmap/',          CareerRoadmapView.as_view()),
    path('career-roadmap/<int:pk>/', CareerRoadmapDetailView.as_view()),

    path('cv/',                   CVBuilderView.as_view()),
    path('cv/build/',             CVBuilderView.as_view()),
    path('cv/<int:pk>/download/', CVDownloadView.as_view()),

    path('mock-interview/start/',   MockInterviewStartView.as_view()),
    path('mock-interview/submit/',  MockInterviewSubmitView.as_view()),
    path('mock-interview/history/', MockInterviewHistoryView.as_view()),
    path('mock-interview/<int:pk>/', MockInterviewDetailView.as_view()),

    path('linkedin/',           LinkedInOptimizerView.as_view()),
    path('linkedin/optimize/',  LinkedInOptimizerView.as_view()),
    path('linkedin/<int:pk>/',  LinkedInOptimizerDetailView.as_view()),

    path('intelligence/career-path/',   CareerPathPredictorView.as_view()),
    path('intelligence/skill-gap/',     SkillGapAnalyzerView.as_view()),
    path('intelligence/market-trends/', MarketTrendsView.as_view()),
    path('intelligence/resume-gap/',    ResumeJobGapView.as_view()),
    path('intelligence/competitor/',    CompetitorAnalysisView.as_view()),
    path('intelligence/history/',       CareerIntelligenceHistoryView.as_view()),
]