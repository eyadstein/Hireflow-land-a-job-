from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Application
from .serializers import ApplicationSerializer


class IsJobOwner(permissions.BasePermission):
    """Only the recruiter who posted the job can update application status."""
    def has_object_permission(self, request, view, obj):
        return obj.job.posted_by == request.user


class ApplyView(generics.CreateAPIView):
    """Job seeker applies to a job."""
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)


class MyApplicationsView(generics.ListAPIView):
    """Job seeker sees their own applications."""
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(applicant=self.request.user)


class JobApplicationsView(generics.ListAPIView):
    """Recruiter sees all applicants for one of their jobs."""
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(
            job_id=self.kwargs['job_id']
        ).order_by('-created_at')


class UpdateStatusView(generics.UpdateAPIView):
    """Recruiter accepts or rejects an applicant (only if they own the job)."""
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsJobOwner]
    queryset = Application.objects.all()
