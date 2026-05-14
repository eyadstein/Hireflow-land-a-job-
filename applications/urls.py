from django.urls import path

from .views import (
    AcceptTopCandidatesView,
    ApplicationDetailView,
    ApplicationListCreateView,
    ApplyView,
    BulkDecisionView,
    CandidateNotesView,
    CandidateProfileView,
    CandidateTimelineView,
    CompareCandidatesView,
    JobApplicationsView,
    MyApplicationsView,
    NoteDetailView,
    RejectAllActiveView,
    RejectAllPendingView,
    UpdateStatusView,
)

urlpatterns = [
    path("apply/", ApplyView.as_view(), name="apply"),
    path("mine/", MyApplicationsView.as_view(), name="my_applications"),
    path("job/<int:job_id>/", JobApplicationsView.as_view(), name="job_applications"),
    path("<int:pk>/status/", UpdateStatusView.as_view(), name="update_application_status"),

    path("candidate/<int:user_id>/profile/", CandidateProfileView.as_view(), name="candidate_profile"),
    path("candidate/<int:user_id>/timeline/", CandidateTimelineView.as_view(), name="candidate_timeline"),
    path("candidate/<int:user_id>/notes/", CandidateNotesView.as_view(), name="candidate_notes"),
    path("notes/<int:note_id>/", NoteDetailView.as_view(), name="candidate_note_detail"),

    path("compare/", CompareCandidatesView.as_view(), name="compare_candidates"),
    path("bulk-decision/", BulkDecisionView.as_view(), name="bulk_decision"),

    path("job/<int:job_id>/reject-all-pending/", RejectAllPendingView.as_view(), name="reject_all_pending"),
    path("job/<int:job_id>/reject-all-active/", RejectAllActiveView.as_view(), name="reject_all_active"),
    path("job/<int:job_id>/accept-top/", AcceptTopCandidatesView.as_view(), name="accept_top_candidates"),

    path("", ApplicationListCreateView.as_view(), name="applications"),
    path("<int:pk>/", ApplicationDetailView.as_view(), name="application_detail"),
]