from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
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


# ── Risk and Behavior Alerts (Omar — #45) ──

def generate_alerts(recruiter):
    """Scan all recruiter data and generate risk alerts."""
    alerts = []
    now = timezone.now()

    my_jobs = Job.objects.filter(posted_by=recruiter)
    my_job_ids = my_jobs.values_list('id', flat=True)
    all_apps = Application.objects.filter(job_id__in=my_job_ids)

    for job in my_jobs:
        job_apps = Application.objects.filter(job=job)
        total_apps = job_apps.count()
        pending_apps = job_apps.filter(status='pending').count()
        rejected_apps = job_apps.filter(status='rejected').count()
        accepted_apps = job_apps.filter(status='accepted').count()
        days_posted = (now - job.created_at).days

        # ── Alert 1: Stale job — no applications after 7+ days ──
        if total_apps == 0 and days_posted >= 7:
            alerts.append({
                'type': 'stale_job',
                'severity': 'high',
                'title': 'Stale Job Posting',
                'message': f'"{job.title}" has been posted for {days_posted} days with zero applications.',
                'job_id': job.id,
                'job_title': job.title,
                'action': 'Consider improving the job description, adding salary info, or reposting.',
            })

        # ── Alert 2: Low application rate — posted 3+ days, less than 1 app/day ──
        if days_posted >= 3 and total_apps > 0:
            rate = total_apps / days_posted
            if rate < 0.5:
                alerts.append({
                    'type': 'low_application_rate',
                    'severity': 'medium',
                    'title': 'Low Application Rate',
                    'message': f'"{job.title}" is getting only {round(rate, 2)} applications/day ({total_apps} total in {days_posted} days).',
                    'job_id': job.id,
                    'job_title': job.title,
                    'action': 'Review job listing quality. Add missing fields like salary, requirements, or job type.',
                })

        # ── Alert 3: Unreviewed applications piling up ──
        if pending_apps >= 5:
            alerts.append({
                'type': 'pending_backlog',
                'severity': 'high',
                'title': 'Unreviewed Applications Piling Up',
                'message': f'"{job.title}" has {pending_apps} pending applications waiting for review.',
                'job_id': job.id,
                'job_title': job.title,
                'action': 'Review pending applications soon. Candidates lose interest after 48 hours.',
            })
        elif pending_apps >= 3:
            alerts.append({
                'type': 'pending_backlog',
                'severity': 'medium',
                'title': 'Applications Awaiting Review',
                'message': f'"{job.title}" has {pending_apps} pending applications.',
                'job_id': job.id,
                'job_title': job.title,
                'action': 'Review these applications to keep candidates engaged.',
            })

        # ── Alert 4: High rejection rate ──
        decided = accepted_apps + rejected_apps
        if decided >= 3:
            rejection_rate = round((rejected_apps / decided) * 100)
            if rejection_rate >= 80:
                alerts.append({
                    'type': 'high_rejection_rate',
                    'severity': 'high',
                    'title': 'Very High Rejection Rate',
                    'message': f'"{job.title}" has a {rejection_rate}% rejection rate ({rejected_apps}/{decided} rejected).',
                    'job_id': job.id,
                    'job_title': job.title,
                    'action': 'Your job listing may be attracting the wrong candidates. Clarify requirements and expectations.',
                })
            elif rejection_rate >= 60:
                alerts.append({
                    'type': 'high_rejection_rate',
                    'severity': 'medium',
                    'title': 'High Rejection Rate',
                    'message': f'"{job.title}" has a {rejection_rate}% rejection rate ({rejected_apps}/{decided} rejected).',
                    'job_id': job.id,
                    'job_title': job.title,
                    'action': 'Consider adjusting the job requirements to better match the candidates you want.',
                })

        # ── Alert 5: Old job still open ──
        if days_posted >= 30:
            alerts.append({
                'type': 'old_job',
                'severity': 'low',
                'title': 'Job Posted Over 30 Days Ago',
                'message': f'"{job.title}" has been open for {days_posted} days.',
                'job_id': job.id,
                'job_title': job.title,
                'action': 'Consider closing this position if it has been filled, or refresh the listing.',
            })

        # ── Alert 6: Incomplete job posting ──
        missing_fields = []
        if not job.salary:
            missing_fields.append('salary')
        if not job.description or len(job.description) < 50:
            missing_fields.append('description')
        if not job.location:
            missing_fields.append('location')
        if hasattr(job, 'job_type') and not job.job_type:
            missing_fields.append('job_type')
        if hasattr(job, 'career_level') and not job.career_level:
            missing_fields.append('career_level')
        if hasattr(job, 'requirements') and not job.requirements:
            missing_fields.append('requirements')

        if len(missing_fields) >= 3:
            alerts.append({
                'type': 'incomplete_posting',
                'severity': 'medium',
                'title': 'Incomplete Job Posting',
                'message': f'"{job.title}" is missing {len(missing_fields)} fields: {", ".join(missing_fields)}.',
                'job_id': job.id,
                'job_title': job.title,
                'action': 'Complete the missing fields to improve visibility and attract more candidates.',
            })

    # ── Alert 7: Duplicate applicants (same person applying to many jobs) ──
    from django.db.models import Count
    if my_job_ids:
        duplicate_applicants = (
            Application.objects.filter(job_id__in=my_job_ids)
            .values('applicant__id', 'applicant__username')
            .annotate(app_count=Count('id'))
            .filter(app_count__gte=3)
            .order_by('-app_count')
        )

        for dup in duplicate_applicants:
            alerts.append({
                'type': 'frequent_applicant',
                'severity': 'low',
                'title': 'Frequent Applicant',
                'message': f'{dup["applicant__username"]} has applied to {dup["app_count"]} of your jobs.',
                'user_id': dup['applicant__id'],
                'action': 'This could indicate strong interest or mass-applying. Review their applications carefully.',
            })

    # ── Alert 8: No jobs posted ──
    if my_jobs.count() == 0:
        alerts.append({
            'type': 'no_jobs',
            'severity': 'low',
            'title': 'No Jobs Posted',
            'message': 'You haven\'t posted any jobs yet.',
            'action': 'Create your first job posting to start receiving applications.',
        })

    # Sort by severity: high first, then medium, then low
    severity_order = {'high': 0, 'medium': 1, 'low': 2}
    alerts.sort(key=lambda x: severity_order.get(x['severity'], 3))

    return alerts


class RiskAlertsView(APIView):
    """GET all risk and behavior alerts for the recruiter."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        alerts = generate_alerts(request.user)

        high_count = sum(1 for a in alerts if a['severity'] == 'high')
        medium_count = sum(1 for a in alerts if a['severity'] == 'medium')
        low_count = sum(1 for a in alerts if a['severity'] == 'low')

        return Response({
            'total_alerts': len(alerts),
            'high': high_count,
            'medium': medium_count,
            'low': low_count,
            'needs_attention': high_count > 0,
            'alerts': alerts,
        })