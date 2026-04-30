from django.urls import path
from .views import AgentChatView, ResumeAnalyzerView, CoverLetterView, SalaryEstimatorView, InterviewCoachView

urlpatterns = [
    path('resume/', ResumeAnalyzerView.as_view()),
    path('cover-letter/', CoverLetterView.as_view()),
    path('salary/', SalaryEstimatorView.as_view()),
    path('interview/', InterviewCoachView.as_view()),
    path('chat/', AgentChatView.as_view()),
]