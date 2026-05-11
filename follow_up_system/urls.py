from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FollowUpTemplateViewSet, FollowUpRuleViewSet, FollowUpScheduleViewSet,
    FollowUpHistoryViewSet, FollowUpTriggerViewSet, FollowUpAnalyticsViewSet,
    FollowUpBlacklistViewSet
)

router = DefaultRouter()
router.register(r'templates', FollowUpTemplateViewSet, basename='template')
router.register(r'rules', FollowUpRuleViewSet, basename='rule')
router.register(r'schedules', FollowUpScheduleViewSet, basename='schedule')
router.register(r'history', FollowUpHistoryViewSet, basename='history')
router.register(r'triggers', FollowUpTriggerViewSet, basename='trigger')
router.register(r'analytics', FollowUpAnalyticsViewSet, basename='followup-analytics')
router.register(r'blacklist', FollowUpBlacklistViewSet, basename='blacklist')

urlpatterns = [
    path('', include(router.urls)),
]
