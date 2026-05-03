from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Job
from .serializers import JobSerializer
from .analytics import get_seeker_stats, get_recruiter_stats


class IsRecruiter(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == 'recruiter'


class JobListCreateView(generics.ListCreateAPIView):
    serializer_class   = JobSerializer
    permission_classes = [IsRecruiter]

    def get_queryset(self):
        return Job.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = JobSerializer
    permission_classes = [IsRecruiter]
    queryset           = Job.objects.all()


# ─────────────────────────────────────────────
#  Analytics — Job Seeker
# ─────────────────────────────────────────────
class SeekerStatsView(APIView):
    """
    GET /api/jobs/analytics/my-stats/

    Returns the authenticated job seeker's full dashboard stats:
    - Total applications
    - Breakdown per Kanban status
    - Weekly activity (last 30 days)
    - Top 5 companies applied to
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != 'jobseeker':
            return Response(
                {'detail': 'Only job seekers can access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )
        data = get_seeker_stats(request.user)
        return Response(data)


# ─────────────────────────────────────────────
#  Analytics — Recruiter
# ─────────────────────────────────────────────
class RecruiterStatsView(APIView):
    """
    GET /api/jobs/analytics/recruiter-stats/

    Returns the authenticated recruiter's dashboard:
    - Total jobs posted
    - Total applications received
    - Applications per job
    - 10 most recent applicants
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != 'recruiter':
            return Response(
                {'detail': 'Only recruiters can access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )
        data = get_recruiter_stats(request.user)
        return Response(data)