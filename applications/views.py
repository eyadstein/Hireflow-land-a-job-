from rest_framework import generics, permissions
from .models import Application
from .serializers import ApplicationSerializer


class IsJobOwner(permissions.BasePermission):
    """Only the recruiter who posted the job can update application status."""
    def has_object_permission(self, request, view, obj):
        return obj.job.posted_by == request.user


class ApplyView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)


class MyApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(applicant=self.request.user)


class JobApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(
            job_id=self.kwargs['job_id']
        ).order_by('-created_at')


class UpdateStatusView(generics.UpdateAPIView):
    """Only the recruiter who owns the job can accept/reject."""
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsJobOwner]
    queryset = Application.objects.all()