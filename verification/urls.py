from django.urls import path
from .views import (
    ProfileCompletionView,
    VerifyProfileView,
    BadgeInfoView,
    CanApplyView,
)

urlpatterns = [
    path('completion/', ProfileCompletionView.as_view()),
    path('verify/', VerifyProfileView.as_view()),
    path('badges/', BadgeInfoView.as_view()),
    path('can-apply/', CanApplyView.as_view()),
]