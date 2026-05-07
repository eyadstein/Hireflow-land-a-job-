from django.urls import path
from .views import (
    JobListCreateView,
    JobDetailView,
    RankedCandidatesView,
    StarCandidatesView,
)

urlpatterns = [
    path('', JobListCreateView.as_view()),
    path('<int:pk>/', JobDetailView.as_view()),

    # Top Candidate Identification
    path('<int:job_id>/ranked-candidates/', RankedCandidatesView.as_view()),
    path('star-candidates/', StarCandidatesView.as_view()),
]