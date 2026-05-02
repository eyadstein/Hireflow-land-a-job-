from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import Job
from .serializers import JobSerializer


class IsRecruiter(permissions.BasePermission):
    """Allow read for any authenticated user, write only for recruiters."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == 'recruiter'


class IsJobOwner(permissions.BasePermission):
    """Only the recruiter who posted the job can edit/delete it."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.posted_by == request.user


# ── Existing endpoints (Eyad's) ──

class JobListCreateView(generics.ListCreateAPIView):
    """GET all jobs / POST a new job."""
    serializer_class = JobSerializer
    permission_classes = [IsRecruiter]

    def get_queryset(self):
        return Job.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET / PUT / DELETE a single job."""
    serializer_class = JobSerializer
    permission_classes = [IsRecruiter, IsJobOwner]
    queryset = Job.objects.all()


# ── New recruiter endpoints (Omar's) ──

class RecruiterJobsView(generics.ListAPIView):
    """GET only the logged-in recruiter's own jobs."""
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Job.objects.filter(
            posted_by=self.request.user
        ).order_by('-created_at')


class RecruiterDashboardView(APIView):
    """GET dashboard stats for the logged-in recruiter."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        my_jobs = Job.objects.filter(posted_by=request.user)

        total_jobs = my_jobs.count()

        # Count all applications across recruiter's jobs
        total_applications = sum(
            job.application_set.count() for job in my_jobs
        )

        # Count accepted and decided (accepted + rejected)
        from applications.models import Application
        my_job_ids = my_jobs.values_list('id', flat=True)
        apps = Application.objects.filter(job_id__in=my_job_ids)

        accepted = apps.filter(status='accepted').count()
        decided = apps.filter(status__in=['accepted', 'rejected']).count()
        acceptance_rate = round((accepted / decided) * 100) if decided > 0 else 0

        return Response({
            'total_jobs': total_jobs,
            'total_applications': total_applications,
            'acceptance_rate': acceptance_rate,
        })
