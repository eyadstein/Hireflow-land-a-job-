from django.urls import path
from .views import (
    ApplyView,
    MyApplicationsView,
    JobApplicationsView,
    UpdateStatusView,
    BulkDecisionView,
    RejectAllPendingView,
    AcceptTopCandidatesView,
)

urlpatterns = [
    path('apply/', ApplyView.as_view()),
    path('mine/', MyApplicationsView.as_view()),
    path('job/<int:job_id>/', JobApplicationsView.as_view()),
    path('<int:pk>/status/', UpdateStatusView.as_view()),

    # One Click Decision Actions
    path('bulk-decision/', BulkDecisionView.as_view()),
    path('job/<int:job_id>/reject-all-pending/', RejectAllPendingView.as_view()),
    path('job/<int:job_id>/accept-top/', AcceptTopCandidatesView.as_view()),
]