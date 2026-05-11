from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MarketDataViewSet, SalaryInsightViewSet, DemandAnalysisViewSet,
    SkillsAnalysisViewSet, MarketTrendViewSet, CompensationBenchmarkViewSet,
    MarketReportViewSet, ReportSubscriptionViewSet, MarketAlertViewSet, MarketAnalyticsViewSet
)

router = DefaultRouter()
router.register(r'market-data', MarketDataViewSet, basename='market-data')
router.register(r'salary-insights', SalaryInsightViewSet, basename='salary-insight')
router.register(r'demand-analysis', DemandAnalysisViewSet, basename='demand-analysis')
router.register(r'skills-analysis', SkillsAnalysisViewSet, basename='skills-analysis')
router.register(r'market-trends', MarketTrendViewSet, basename='market-trend')
router.register(r'compensation-benchmarks', CompensationBenchmarkViewSet, basename='compensation-benchmark')
router.register(r'market-reports', MarketReportViewSet, basename='market-report')
router.register(r'report-subscriptions', ReportSubscriptionViewSet, basename='report-subscription')
router.register(r'market-alerts', MarketAlertViewSet, basename='market-alert')

# Analytics-specific endpoints
router.register(r'analytics', MarketAnalyticsViewSet, basename='market-analytics')

urlpatterns = [
    path('', include(router.urls)),
]
