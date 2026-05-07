from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from .models import Application
from .serializers import ApplicationSerializer


class IsJobOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.job.posted_by == request.user


# ── Eyad's existing endpoints ──

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
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsJobOwner]
    queryset = Application.objects.all()


# ── One Click Decision Actions (Omar — #47) ──

class BulkDecisionView(APIView):
    """POST to accept or reject multiple applications at once."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        application_ids = request.data.get('application_ids', [])
        decision = request.data.get('decision', '')

        if not application_ids or not isinstance(application_ids, list):
            return Response(
                {'error': 'Provide a list of application_ids.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if decision not in ['accepted', 'rejected']:
            return Response(
                {'error': 'Decision must be "accepted" or "rejected".'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from jobs.models import Job
        my_job_ids = Job.objects.filter(
            posted_by=request.user
        ).values_list('id', flat=True)

        # Only update applications for jobs the recruiter owns
        apps = Application.objects.filter(
            id__in=application_ids,
            job_id__in=my_job_ids,
            status='pending'
        )

        if not apps.exists():
            return Response(
                {'error': 'No valid pending applications found for the given IDs.'},
                status=status.HTTP_404_NOT_FOUND
            )

        updated_count = apps.count()
        updated_ids = list(apps.values_list('id', flat=True))
        apps.update(status=decision)

        return Response({
            'decision': decision,
            'updated_count': updated_count,
            'updated_ids': updated_ids,
            'message': f'{updated_count} application(s) {decision} successfully.',
        })


class RejectAllPendingView(APIView):
    """POST to reject all pending applications for a specific job."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, job_id):
        from jobs.models import Job
        job = Job.objects.filter(id=job_id, posted_by=request.user).first()

        if not job:
            return Response(
                {'error': 'Job not found or not owned by you.'},
                status=status.HTTP_404_NOT_FOUND
            )

        pending_apps = Application.objects.filter(
            job=job,
            status='pending'
        )

        count = pending_apps.count()

        if count == 0:
            return Response({
                'message': 'No pending applications to reject.',
                'rejected_count': 0,
            })

        pending_apps.update(status='rejected')

        return Response({
            'job_id': job.id,
            'job_title': job.title,
            'rejected_count': count,
            'message': f'All {count} pending application(s) rejected for "{job.title}".',
        })


class AcceptTopCandidatesView(APIView):
    """POST to accept top N candidates and reject the rest for a job."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, job_id):
        from jobs.models import Job
        job = Job.objects.filter(id=job_id, posted_by=request.user).first()

        if not job:
            return Response(
                {'error': 'Job not found or not owned by you.'},
                status=status.HTTP_404_NOT_FOUND
            )

        top_n = request.data.get('top_n', 1)

        if not isinstance(top_n, int) or top_n < 1:
            return Response(
                {'error': 'top_n must be a positive integer.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        pending_apps = Application.objects.filter(
            job=job,
            status='pending'
        ).order_by('created_at')

        total_pending = pending_apps.count()

        if total_pending == 0:
            return Response({
                'message': 'No pending applications to process.',
                'accepted_count': 0,
                'rejected_count': 0,
            })

        # Accept the first N (earliest applicants), reject the rest
        to_accept = list(pending_apps[:top_n].values_list('id', flat=True))
        to_reject = list(pending_apps[top_n:].values_list('id', flat=True))

        Application.objects.filter(id__in=to_accept).update(status='accepted')
        Application.objects.filter(id__in=to_reject).update(status='rejected')

        return Response({
            'job_id': job.id,
            'job_title': job.title,
            'accepted_count': len(to_accept),
            'rejected_count': len(to_reject),
            'accepted_ids': to_accept,
            'rejected_ids': to_reject,
            'message': f'Accepted top {len(to_accept)}, rejected {len(to_reject)} for "{job.title}".',
        })