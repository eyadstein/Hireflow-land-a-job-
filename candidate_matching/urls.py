from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CandidateProfileViewSet, JobRequirementViewSet, CandidateMatchViewSet,
    MatchingAlgorithmViewSet, MatchHistoryViewSet
)

router = DefaultRouter()
router.register(r'profiles', CandidateProfileViewSet, basename='matching-profile')
router.register(r'requirements', JobRequirementViewSet, basename='requirement')
router.register(r'matches', CandidateMatchViewSet, basename='match')
router.register(r'algorithms', MatchingAlgorithmViewSet, basename='algorithm')
router.register(r'history', MatchHistoryViewSet, basename='matching-history')

urlpatterns = [
    path('', include(router.urls)),
]
