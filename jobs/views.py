from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Job, SavedJob
from .serializers import JobSerializer, SavedJobSerializer
from django.db import models as django_models


class IsRecruiter(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return (
            request.user.is_authenticated and
            request.user.role == 'recruiter'
        )


class JobListCreateView(generics.ListCreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsRecruiter]

    def get_queryset(self):
        return Job.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsRecruiter]
    queryset = Job.objects.all()


# ── Saved Jobs ─────────────────────────────────────────────────

class SavedJobListView(generics.ListAPIView):
    serializer_class = SavedJobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user)


class SaveJobView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Save a job"""
        job_id = request.data.get('job_id')
        if not job_id:
            return Response(
                {'error': 'job_id is required'},
                status=400
            )

        saved, created = SavedJob.objects.get_or_create(
            user=request.user,
            job_id=job_id,
            defaults={
                'title': request.data.get('title', ''),
                'company': request.data.get('company', ''),
                'location': request.data.get('location', ''),
                'apply_link': request.data.get('apply_link') or None,
                'salary_min': request.data.get('salary_min'),
                'salary_max': request.data.get('salary_max'),
                'source': request.data.get('source', ''),
                'experience_level': request.data.get('experience_level', ''),
                'job_type': request.data.get('job_type', ''),
                'logo': request.data.get('logo') or None,
                'is_remote': request.data.get('is_remote', False),
                'notes': request.data.get('notes', ''),
            }
        )

        if not created:
            return Response({
                'message': 'Job already saved',
                'saved': False,
                'job': SavedJobSerializer(saved).data,
            })

        return Response({
            'message': 'Job saved successfully',
            'saved': True,
            'job': SavedJobSerializer(saved).data,
        }, status=201)

    def delete(self, request):
        """Unsave a job"""
        job_id = request.data.get('job_id')
        if not job_id:
            return Response(
                {'error': 'job_id is required'},
                status=400
            )

        deleted_count, _ = SavedJob.objects.filter(
            user=request.user,
            job_id=job_id
        ).delete()

        if deleted_count:
            return Response({
                'message': 'Job removed from saved',
                'removed': True
            })
        return Response({
            'message': 'Job not found in saved',
            'removed': False
        })


class CheckSavedJobView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, job_id):
        """Check if a specific job is saved"""
        is_saved = SavedJob.objects.filter(
            user=request.user,
            job_id=job_id
        ).exists()
        return Response({
            'is_saved': is_saved,
            'job_id': job_id
        })


class SavedJobNotesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, job_id):
        """Update notes for a saved job"""
        notes = request.data.get('notes', '')
        try:
            saved = SavedJob.objects.get(
                user=request.user,
                job_id=job_id
            )
            saved.notes = notes
            saved.save()
            return Response({
                'message': 'Notes updated successfully',
                'notes': notes
            })
        except SavedJob.DoesNotExist:
            return Response(
                {'error': 'Saved job not found'},
                status=404
            )


class SavedJobStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get stats about user's saved jobs"""
        saved = SavedJob.objects.filter(user=request.user)
        return Response({
            'total_saved': saved.count(),
            'by_source': {
                item['source']: item['count']
                for item in saved.values('source').annotate(
                    count=models.Count('id')
                )
            },
            'by_level': {
                item['experience_level']: item['count']
                for item in saved.values('experience_level').annotate(
                    count=models.Count('id')
                )
            },
            'remote_count': saved.filter(is_remote=True).count(),
        })