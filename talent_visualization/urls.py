from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TalentPoolViewSet, TalentPoolCandidateViewSet, TalentVisualizationViewSet,
    TalentAnalyticsViewSet, TalentDashboardViewSet, UserDashboardViewSet,
    TalentReportViewSet, ReportScheduleViewSet, TalentInsightViewSet, AnalyticsViewSet
)

router = DefaultRouter()
router.register(r'pools', TalentPoolViewSet, basename='pool')
router.register(r'pool-candidates', TalentPoolCandidateViewSet, basename='pool-candidate')
router.register(r'visualizations', TalentVisualizationViewSet, basename='visualization')
router.register(r'analytics', TalentAnalyticsViewSet, basename='analytics')
router.register(r'dashboards', TalentDashboardViewSet, basename='dashboard')
router.register(r'user-dashboards', UserDashboardViewSet, basename='user-dashboard')
router.register(r'reports', TalentReportViewSet, basename='report')
router.register(r'report-schedules', ReportScheduleViewSet, basename='report-schedule')
router.register(r'insights', TalentInsightViewSet, basename='vis-insight')

# Analytics-specific endpoints
router.register(r'analytics-data', AnalyticsViewSet, basename='analytics-data')

urlpatterns = [
    path('', include(router.urls)),
]
