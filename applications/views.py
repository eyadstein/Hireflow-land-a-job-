from rest_framework import generics, permissions
from .models import Application
from .serializers import ApplicationSerializer
from verification.services import can_apply_to_job

class ApplyView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Check if user can apply
        allowed, reason = can_apply_to_job(self.request.user)
        if not allowed:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(detail=reason)
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
        return Application.objects.filter(job_id=self.kwargs['job_id'])

class UpdateStatusView(generics.UpdateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Application.objects.all()