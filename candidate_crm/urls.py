from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CandidateProfileViewSet, CandidateInteractionViewSet, CandidateTaskViewSet,
    CandidateDocumentViewSet, CandidatePipelineViewSet, CandidatePipelineStageViewSet,
    CandidateTagViewSet, CandidateEmailViewSet, CandidateActivityViewSet,
    CandidateRelationshipViewSet, CandidateSearchViewSet, CandidateAnalyticsViewSet
)

router = DefaultRouter()
router.register(r'profiles', CandidateProfileViewSet, basename='profile')
router.register(r'interactions', CandidateInteractionViewSet, basename='interaction')
router.register(r'tasks', CandidateTaskViewSet, basename='task')
router.register(r'documents', CandidateDocumentViewSet, basename='document')
router.register(r'pipelines', CandidatePipelineViewSet, basename='pipeline')
router.register(r'pipeline-stages', CandidatePipelineStageViewSet, basename='pipeline-stage')
router.register(r'tags', CandidateTagViewSet, basename='tag')
router.register(r'emails', CandidateEmailViewSet, basename='email')
router.register(r'activities', CandidateActivityViewSet, basename='activity')
router.register(r'relationships', CandidateRelationshipViewSet, basename='relationship')
router.register(r'search', CandidateSearchViewSet, basename='search')
router.register(r'analytics', CandidateAnalyticsViewSet, basename='analytics')

urlpatterns = [
    path('', include(router.urls)),
]
