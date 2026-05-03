from django.urls import path
from .views import (
    MyReferralCodeView,
    ReferralStatsView,
    MyReferralsView,
    ValidateReferralCodeView,
    ApplyReferralView,
)

urlpatterns = [
    path('my-code/', MyReferralCodeView.as_view()),
    path('stats/', ReferralStatsView.as_view()),
    path('my-referrals/', MyReferralsView.as_view()),
    path('validate/', ValidateReferralCodeView.as_view()),
    path('apply/', ApplyReferralView.as_view()),
]