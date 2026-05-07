from django.urls import path
from .views import (
    JobListCreateView,
    JobDetailView,
    RiskAlertsView,
)

urlpatterns = [
    path('', JobListCreateView.as_view()),
    path('<int:pk>/', JobDetailView.as_view()),

    # Risk and Behavior Alerts
    path('alerts/', RiskAlertsView.as_view()),
]