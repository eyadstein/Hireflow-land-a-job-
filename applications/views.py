from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Application, CandidateNote
from .serializers import ApplicationSerializer, CandidateNoteSerializer

User = get_user_model()


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


# ── Candidate Insight Panel (Omar — #37) ──

class CandidateProfileView(APIView):
    """GET full 360 profile of a candidate."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        candidate = get_object_or_404(User, id=user_id)

        from jobs.models import Job
        my_job_ids = Job.objects.filter(
            posted_by=request.user
        ).values_list('id', flat=True)

        apps = Application.objects.filter(
            applicant=candidate,
            job_id__in=my_job_ids
        ).order_by('-created_at')

        pending = apps.filter(status='pending').count()
        accepted = apps.filter(status='accepted').count()
        rejected = apps.filter(status='rejected').count()

        notes_count = CandidateNote.objects.filter(
            candidate=candidate,
            recruiter=request.user
        ).count()

        return Response({
            'user_id': candidate.id,
            'username': candidate.username,
            'email': candidate.email,
            'total_applications': apps.count(),
            'pending': pending,
            'accepted': accepted,
            'rejected': rejected,
            'first_applied': apps.last().created_at.isoformat() if apps.exists() else None,
            'last_applied': apps.first().created_at.isoformat() if apps.exists() else None,
            'applications': ApplicationSerializer(apps, many=True).data,
            'notes_count': notes_count,
        })


class CandidateTimelineView(APIView):
    """GET chronological timeline of all candidate interactions."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        candidate = get_object_or_404(User, id=user_id)

        from jobs.models import Job
        my_job_ids = Job.objects.filter(
            posted_by=request.user
        ).values_list('id', flat=True)

        apps = Application.objects.filter(
            applicant=candidate,
            job_id__in=my_job_ids
        ).select_related('job')

        notes = CandidateNote.objects.filter(
            candidate=candidate,
            recruiter=request.user
        )

        timeline = []

        for app in apps:
            timeline.append({
                'type': 'application',
                'date': app.created_at.isoformat(),
                'description': f"Applied to {app.job.title} at {app.job.company}",
                'status': app.status,
                'job_id': app.job.id,
            })

        for note in notes:
            timeline.append({
                'type': 'note',
                'date': note.created_at.isoformat(),
                'description': note.content[:100],
                'note_id': note.id,
            })

        timeline.sort(key=lambda x: x['date'], reverse=True)

        return Response({
            'candidate_id': candidate.id,
            'candidate_name': candidate.username,
            'timeline': timeline,
        })


class CandidateNotesView(APIView):
    """GET all notes or POST a new note for a candidate."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        candidate = get_object_or_404(User, id=user_id)
        notes = CandidateNote.objects.filter(
            candidate=candidate,
            recruiter=request.user
        )
        serializer = CandidateNoteSerializer(notes, many=True)
        return Response(serializer.data)

    def post(self, request, user_id):
        candidate = get_object_or_404(User, id=user_id)
        content = request.data.get('content', '').strip()

        if not content:
            return Response(
                {'error': 'Note content is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        note = CandidateNote.objects.create(
            candidate=candidate,
            recruiter=request.user,
            content=content
        )

        serializer = CandidateNoteSerializer(note)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class NoteDetailView(APIView):
    """PUT to edit or DELETE a recruiter note."""
    permission_classes = [permissions.IsAuthenticated]

    def get_note(self, note_id, user):
        return get_object_or_404(CandidateNote, id=note_id, recruiter=user)

    def put(self, request, note_id):
        note = self.get_note(note_id, request.user)
        content = request.data.get('content', '').strip()

        if not content:
            return Response(
                {'error': 'Note content is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        note.content = content
        note.save()
        serializer = CandidateNoteSerializer(note)
        return Response(serializer.data)

    def delete(self, request, note_id):
        note = self.get_note(note_id, request.user)
        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)