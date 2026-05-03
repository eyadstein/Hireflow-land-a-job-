from django.urls import path
from .views import (
    SendEmailOTPView,
    SendPhoneOTPView,
    VerifyEmailOTPView,
    VerifyPhoneOTPView,
    OTPStatusView,
)

urlpatterns = [
    path('send/email/', SendEmailOTPView.as_view()),
    path('send/phone/', SendPhoneOTPView.as_view()),
    path('verify/email/', VerifyEmailOTPView.as_view()),
    path('verify/phone/', VerifyPhoneOTPView.as_view()),
    path('status/', OTPStatusView.as_view()),
]