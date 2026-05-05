from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    SecureLoginView,
    ProfileView,
    AllUsersView,
    LogoutView,
    SecurityAuditLogView,
    TwoFactorSetupView,
    TwoFactorVerifyView,
    TwoFactorDisableView,
)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/',    SecureLoginView.as_view()),
    path('refresh/',  TokenRefreshView.as_view()),
    path('profile/',  ProfileView.as_view()),
    path('all/',      AllUsersView.as_view()),

    path('logout/',       LogoutView.as_view()),
    path('security-log/', SecurityAuditLogView.as_view()),

    path('2fa/setup/',    TwoFactorSetupView.as_view()),
    path('2fa/verify/',   TwoFactorVerifyView.as_view()),
    path('2fa/disable/',  TwoFactorDisableView.as_view()),
]