from django.urls import path
from .views import (
    ApplyView,
    MyApplicationsView,
    JobApplicationsView,
    UpdateStatusView,
    CandidateProfileView,
    CandidateTimelineView,
    CandidateNotesView,
    NoteDetailView,
    CompareCandidatesView,
    BulkDecisionView,
    RejectAllPendingView,
    AcceptTopCandidatesView,
    ApplicationListCreateView,
    ApplicationDetailView,
)

urlpatterns = [
    path('apply/', ApplyView.as_view()),
    path('mine/', MyApplicationsView.as_view()),
    path('job/<int:job_id>/', JobApplicationsView.as_view()),
    path('<int:pk>/status/', UpdateStatusView.as_view()),

    # Candidate Insight Panel
    path('candidate/<int:user_id>/profile/', CandidateProfileView.as_view()),
    path('candidate/<int:user_id>/timeline/', CandidateTimelineView.as_view()),
    path('candidate/<int:user_id>/notes/', CandidateNotesView.as_view()),
    path('notes/<int:note_id>/', NoteDetailView.as_view()),

    # Candidate Comparison Tool
    path('compare/', CompareCandidatesView.as_view()),

    # One Click Decision Actions
    path('bulk-decision/', BulkDecisionView.as_view()),
    path('job/<int:job_id>/reject-all-pending/', RejectAllPendingView.as_view()),
    path('job/<int:job_id>/accept-top/', AcceptTopCandidatesView.as_view()),

    # Application tracker (from integration/frontend-backend)
    path('', ApplicationListCreateView.as_view()),
    path('<int:pk>/', ApplicationDetailView.as_view()),
]
