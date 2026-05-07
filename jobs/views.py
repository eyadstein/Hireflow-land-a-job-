from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Job
from .serializers import JobSerializer
from applications.models import Application


class IsRecruiter(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == 'recruiter'


class IsJobOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.posted_by == request.user


# ── Eyad's existing endpoints ──

class JobListCreateView(generics.ListCreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsRecruiter]

    def get_queryset(self):
        return Job.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsRecruiter, IsJobOwner]
    queryset = Job.objects.all()


# ── Top Candidate Identification (Omar — #39) ──

def calculate_candidate_score(applicant, job, application):
    """
    Score a candidate 0-100 based on multiple signals.
    Higher = better candidate.
    """
    score = 0

    # 1. Application recency (max 25 points)
    # Applied within 24h of posting = 25, within 3 days = 20, within 7 days = 15, else 5
    if job.created_at and application.created_at:
        hours_after_posting = (application.created_at - job.created_at).total_seconds() / 3600
        if hours_after_posting <= 24:
            score += 25
        elif hours_after_posting <= 72:
            score += 20
        elif hours_after_posting <= 168:
            score += 15
        else:
            score += 5

    # 2. Past acceptance rate (max 25 points)
    # If this candidate was accepted in other jobs, they're likely good
    all_apps = Application.objects.filter(applicant=applicant)
    total_decided = all_apps.filter(status__in=['accepted', 'rejected']).count()
    accepted = all_apps.filter(status='accepted').count()
    if total_decided > 0:
        past_rate = accepted / total_decided
        score += round(past_rate * 25)
    else:
        score += 10  # neutral for first-time applicants

    # 3. Application engagement (max 20 points)
    # Candidates who apply to multiple jobs show interest in the platform
    total_applications = all_apps.count()
    if total_applications >= 5:
        score += 20
    elif total_applications >= 3:
        score += 15
    elif total_applications >= 2:
        score += 10
    else:
        score += 5

    # 4. Profile completeness (max 15 points)
    # Check if user has filled in their profile fields
    completeness = 0
    if applicant.email:
        completeness += 5
    if applicant.first_name:
        completeness += 5
    if applicant.last_name:
        completeness += 5
    score += completeness

    # 5. Recency of account (max 15 points)
    # Newer active accounts get a small boost
    if applicant.date_joined:
        days_since_joined = (timezone.now() - applicant.date_joined).days
        if days_since_joined <= 30:
            score += 15
        elif days_since_joined <= 90:
            score += 12
        elif days_since_joined <= 365:
            score += 8
        else:
            score += 5

    return min(score, 100)


def get_candidate_tier(score):
    """Classify candidate into a tier based on score."""
    if score >= 80:
        return 'star'
    elif score >= 60:
        return 'strong'
    elif score >= 40:
        return 'average'
    else:
        return 'below_average'


class RankedCandidatesView(APIView):
    """GET all applicants for a specific job, ranked by score."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, job_id):
        job = Job.objects.filter(id=job_id, posted_by=request.user).first()
        if not job:
            return Response({'error': 'Job not found or not owned by you.'}, status=404)

        applications = Application.objects.filter(job=job).select_related('applicant')

        candidates = []
        for app in applications:
            score = calculate_candidate_score(app.applicant, job, app)
            tier = get_candidate_tier(score)

            candidates.append({
                'application_id': app.id,
                'user_id': app.applicant.id,
                'username': app.applicant.username,
                'email': app.applicant.email,
                'first_name': app.applicant.first_name,
                'last_name': app.applicant.last_name,
                'status': app.status,
                'applied_at': app.created_at.isoformat(),
                'score': score,
                'tier': tier,
                'is_star': tier == 'star',
            })

        # Sort by score descending
        candidates.sort(key=lambda x: x['score'], reverse=True)

        # Add rank
        for i, c in enumerate(candidates):
            c['rank'] = i + 1

        return Response({
            'job_id': job.id,
            'job_title': job.title,
            'company': job.company,
            'total_candidates': len(candidates),
            'star_count': sum(1 for c in candidates if c['is_star']),
            'candidates': candidates,
        })


class StarCandidatesView(APIView):
    """GET top-scoring candidates across ALL of the recruiter's jobs."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        my_jobs = Job.objects.filter(posted_by=request.user)

        all_star_candidates = []
        seen_users = set()

        for job in my_jobs:
            applications = Application.objects.filter(job=job).select_related('applicant')

            for app in applications:
                if app.applicant.id in seen_users:
                    continue

                score = calculate_candidate_score(app.applicant, job, app)
                tier = get_candidate_tier(score)

                if tier in ['star', 'strong']:
                    seen_users.add(app.applicant.id)

                    # Count total applications to recruiter's jobs
                    apps_to_my_jobs = Application.objects.filter(
                        applicant=app.applicant,
                        job__in=my_jobs
                    )

                    all_star_candidates.append({
                        'user_id': app.applicant.id,
                        'username': app.applicant.username,
                        'email': app.applicant.email,
                        'first_name': app.applicant.first_name,
                        'last_name': app.applicant.last_name,
                        'score': score,
                        'tier': tier,
                        'is_star': tier == 'star',
                        'total_applications_to_you': apps_to_my_jobs.count(),
                        'accepted_by_you': apps_to_my_jobs.filter(status='accepted').count(),
                        'latest_application': app.created_at.isoformat(),
                        'applied_to_job': job.title,
                    })

        all_star_candidates.sort(key=lambda x: x['score'], reverse=True)

        return Response({
            'total_star_candidates': sum(1 for c in all_star_candidates if c['is_star']),
            'total_strong_candidates': sum(1 for c in all_star_candidates if c['tier'] == 'strong'),
            'candidates': all_star_candidates,
        })