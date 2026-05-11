from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TalentPoolViewSet, TalentCandidateViewSet, TalentSearchViewSet,
    TalentEngagementViewSet, TalentCampaignViewSet, TalentInsightViewSet,
    TalentSourceViewSet, TalentSourcingRuleViewSet, TalentAnalyticsViewSet
)

router = DefaultRouter()
router.register(r'pools', TalentPoolViewSet, basename='pool')
router.register(r'candidates', TalentCandidateViewSet, basename='candidate')
router.register(r'searches', TalentSearchViewSet, basename='search')
router.register(r'engagements', TalentEngagementViewSet, basename='engagement')
router.register(r'campaigns', TalentCampaignViewSet, basename='campaign')
router.register(r'insights', TalentInsightViewSet, basename='insight')
router.register(r'sources', TalentSourceViewSet, basename='source')
router.register(r'sourcing-rules', TalentSourcingRuleViewSet, basename='sourcing-rule')
router.register(r'analytics', TalentAnalyticsViewSet, basename='talent-analytics')

urlpatterns = [
    path('', include(router.urls)),
]
