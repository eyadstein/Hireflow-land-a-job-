from django.urls import path
from .views import (
    PlanStatusView,
    PlanCompareView,
    RequestUpgradeView,
    AdminApproveUpgradeView,
)

urlpatterns = [
    path('status/', PlanStatusView.as_view()),
    path('compare/', PlanCompareView.as_view()),
    path('upgrade/', RequestUpgradeView.as_view()),
    path('upgrade/<int:request_id>/approve/', AdminApproveUpgradeView.as_view()),
]