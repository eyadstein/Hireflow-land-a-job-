from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HiringTeamViewSet, HiringDecisionViewSet, InterviewScheduleViewSet,
    CandidateFeedbackViewSet, HiringWorkflowViewSet, JobWorkflowViewSet,
    TeamCollaborationViewSet, InterviewKitViewSet, JobInterviewKitViewSet,
    HiringAnalyticsViewSet, TeamNotificationViewSet
)

router = DefaultRouter()
router.register(r'teams', HiringTeamViewSet, basename='team')
router.register(r'decisions', HiringDecisionViewSet, basename='decision')
router.register(r'interviews', InterviewScheduleViewSet, basename='interview')
router.register(r'feedback', CandidateFeedbackViewSet, basename='feedback')
router.register(r'workflows', HiringWorkflowViewSet, basename='workflow')
router.register(r'job-workflows', JobWorkflowViewSet, basename='job-workflow')
router.register(r'collaborations', TeamCollaborationViewSet, basename='collaboration')
router.register(r'interview-kits', InterviewKitViewSet, basename='interview-kit')
router.register(r'job-interview-kits', JobInterviewKitViewSet, basename='job-interview-kit')
router.register(r'analytics', HiringAnalyticsViewSet, basename='hiring-analytics')
router.register(r'notifications', TeamNotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
