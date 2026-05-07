from django.urls import path
from .views import (
    JobListCreateView,
    JobDetailView,
    JobOptimizeView,
    OptimizationReportView,
)

urlpatterns = [
    path('', JobListCreateView.as_view()),
    path('<int:pk>/', JobDetailView.as_view()),

    # Job Performance Optimization
    path('<int:job_id>/optimize/', JobOptimizeView.as_view()),
    path('optimization-report/', OptimizationReportView.as_view()),
]