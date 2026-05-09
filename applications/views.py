from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Application, CandidateNote
from .serializers import ApplicationSerializer, CandidateNoteSerializer

User = get_user_model()


class IsJobOwner(permissions.BasePermission):
    """Only the recruiter who posted the job can update application status."""
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
    """Recruiter accepts or rejects — stamps reviewed_at timestamp."""
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsJobOwner]
    queryset = Application.objects.all()

    def perform_update(self, serializer):
        serializer.save(reviewed_at=timezone.now())


# ── Candidate Insight Panel endpoints ──

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


# ── Candidate Comparison Tool endpoints ──

def build_candidate_profile(candidate, recruiter_job_ids):
    """Build a full comparison profile for one candidate."""
    apps = Application.objects.filter(
        applicant=candidate,
        job_id__in=recruiter_job_ids
    ).select_related('job')

    total = apps.count()
    pending = apps.filter(status='pending').count()
    accepted = apps.filter(status='accepted').count()
    rejected = apps.filter(status='rejected').count()

    score = 0

    all_apps = Application.objects.filter(applicant=candidate)
    all_decided = all_apps.filter(status__in=['accepted', 'rejected']).count()
    all_accepted = all_apps.filter(status='accepted').count()
    if all_decided > 0:
        score += round((all_accepted / all_decided) * 30)
    else:
        score += 12

    total_all = all_apps.count()
    if total_all >= 5:
        score += 25
    elif total_all >= 3:
        score += 18
    elif total_all >= 2:
        score += 12
    else:
        score += 6

    if candidate.email:
        score += 7
    if candidate.first_name:
        score += 7
    if candidate.last_name:
        score += 6

    if candidate.date_joined:
        days = (timezone.now() - candidate.date_joined).days
        if days <= 30:
            score += 15
        elif days <= 90:
            score += 12
        elif days <= 365:
            score += 8
        else:
            score += 5

    if apps.exists():
        latest = apps.order_by('-created_at').first()
        hours_ago = (timezone.now() - latest.created_at).total_seconds() / 3600
        if hours_ago <= 24:
            score += 10
        elif hours_ago <= 72:
            score += 7
        elif hours_ago <= 168:
            score += 4
        else:
            score += 2

    score = min(score, 100)

    strengths = []
    weaknesses = []

    if all_accepted > 0:
        strengths.append("Previously accepted by recruiters")
    if total_all >= 3:
        strengths.append("Active on platform — applied to multiple jobs")
    if candidate.first_name and candidate.last_name:
        strengths.append("Complete profile")
    else:
        weaknesses.append("Incomplete profile — missing name")
    if pending > 0:
        weaknesses.append(f"{pending} pending application(s) still awaiting review")
    if rejected > 0:
        weaknesses.append(f"Rejected {rejected} time(s)")
    if accepted > 0:
        strengths.append(f"Accepted {accepted} time(s) by you")

    applied_jobs = [
        {
            'job_id': app.job.id,
            'title': app.job.title,
            'company': app.job.company,
            'status': app.status,
            'applied_at': app.created_at.isoformat(),
        }
        for app in apps.order_by('-created_at')
    ]

    return {
        'user_id': candidate.id,
        'username': candidate.username,
        'email': candidate.email,
        'first_name': candidate.first_name or '',
        'last_name': candidate.last_name or '',
        'score': score,
        'tier': 'star' if score >= 80 else 'strong' if score >= 60 else 'average' if score >= 40 else 'below_average',
        'stats': {
            'total_applications': total,
            'pending': pending,
            'accepted': accepted,
            'rejected': rejected,
        },
        'strengths': strengths,
        'weaknesses': weaknesses,
        'applied_jobs': applied_jobs,
    }


class CompareCandidatesView(APIView):
    """POST with candidate_ids to get side-by-side comparison."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        candidate_ids = request.data.get('candidate_ids', [])

        if not candidate_ids or not isinstance(candidate_ids, list):
            return Response(
                {'error': 'Provide a list of candidate_ids (2-4 IDs).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(candidate_ids) < 2:
            return Response(
                {'error': 'Need at least 2 candidates to compare.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(candidate_ids) > 4:
            return Response(
                {'error': 'Maximum 4 candidates can be compared at once.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from jobs.models import Job
        my_job_ids = Job.objects.filter(
            posted_by=request.user
        ).values_list('id', flat=True)

        candidates = User.objects.filter(id__in=candidate_ids)

        if candidates.count() != len(candidate_ids):
            return Response(
                {'error': 'One or more candidate IDs not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        profiles = []
        for candidate in candidates:
            profile = build_candidate_profile(candidate, my_job_ids)
            profiles.append(profile)

        profiles.sort(key=lambda x: x['score'], reverse=True)

        for i, p in enumerate(profiles):
            p['rank'] = i + 1

        best = profiles[0]
        recommendation = {
            'recommended_candidate': best['username'],
            'user_id': best['user_id'],
            'score': best['score'],
            'reason': f"Highest score ({best['score']}/100) with {len(best['strengths'])} strengths and {len(best['weaknesses'])} weaknesses.",
        }

        return Response({
            'total_compared': len(profiles),
            'candidates': profiles,
            'recommendation': recommendation,
        })
