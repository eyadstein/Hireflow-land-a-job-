from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Q
from django.db.models.functions import TruncDate, TruncWeek
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


# ── Omar's recruiter portal endpoints ──

class RecruiterJobsView(generics.ListAPIView):
    """GET only the logged-in recruiter's own jobs."""
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Job.objects.filter(
            posted_by=self.request.user
        ).order_by('-created_at')


class RecruiterDashboardView(APIView):
    """GET basic dashboard stats."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        my_jobs = Job.objects.filter(posted_by=request.user)
        my_job_ids = my_jobs.values_list('id', flat=True)
        apps = Application.objects.filter(job_id__in=my_job_ids)

        total_jobs = my_jobs.count()
        total_applications = apps.count()
        accepted = apps.filter(status='accepted').count()
        decided = apps.filter(status__in=['accepted', 'rejected']).count()
        acceptance_rate = round((accepted / decided) * 100) if decided > 0 else 0

        return Response({
            'total_jobs': total_jobs,
            'total_applications': total_applications,
            'acceptance_rate': acceptance_rate,
        })


# ── Hiring Intelligence & Insights endpoints ──

class ApplicationTrendsView(APIView):
    """GET daily application counts for the last 30 days."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        my_job_ids = Job.objects.filter(
            posted_by=request.user
        ).values_list('id', flat=True)

        thirty_days_ago = timezone.now() - timedelta(days=30)

        trends = (
            Application.objects.filter(
                job_id__in=my_job_ids,
                created_at__gte=thirty_days_ago
            )
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )

        return Response({
            'period': 'last_30_days',
            'data': [
                {'date': t['date'].isoformat(), 'applications': t['count']}
                for t in trends
            ],
        })


class JobTypeDistributionView(APIView):
    """GET breakdown of recruiter's jobs by type."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        my_jobs = Job.objects.filter(posted_by=request.user)

        distribution = (
            my_jobs
            .values('job_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        total = my_jobs.count()

        return Response({
            'total_jobs': total,
            'distribution': [
                {
                    'job_type': d['job_type'] or 'Not specified',
                    'count': d['count'],
                    'percentage': round((d['count'] / total) * 100) if total > 0 else 0,
                }
                for d in distribution
            ],
        })


class TopPerformingJobsView(APIView):
    """GET top 5 jobs by application count."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        my_jobs = (
            Job.objects.filter(posted_by=request.user)
            .annotate(app_count=Count('application'))
            .order_by('-app_count')[:5]
        )

        return Response({
            'top_jobs': [
                {
                    'id': job.id,
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'job_type': job.job_type,
                    'applications': job.app_count,
                    'created_at': job.created_at.isoformat(),
                }
                for job in my_jobs
            ],
        })


class StatusBreakdownView(APIView):
    """GET pending vs accepted vs rejected counts."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        my_job_ids = Job.objects.filter(
            posted_by=request.user
        ).values_list('id', flat=True)

        apps = Application.objects.filter(job_id__in=my_job_ids)

        pending = apps.filter(status='pending').count()
        accepted = apps.filter(status='accepted').count()
        rejected = apps.filter(status='rejected').count()
        total = pending + accepted + rejected

        return Response({
            'total': total,
            'pending': pending,
            'accepted': accepted,
            'rejected': rejected,
            'pending_pct': round((pending / total) * 100) if total > 0 else 0,
            'accepted_pct': round((accepted / total) * 100) if total > 0 else 0,
            'rejected_pct': round((rejected / total) * 100) if total > 0 else 0,
        })


class HiringVelocityView(APIView):
    """GET weekly accepted hires for the last 8 weeks."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        my_job_ids = Job.objects.filter(
            posted_by=request.user
        ).values_list('id', flat=True)

        eight_weeks_ago = timezone.now() - timedelta(weeks=8)

        velocity = (
            Application.objects.filter(
                job_id__in=my_job_ids,
                status='accepted',
                created_at__gte=eight_weeks_ago
            )
            .annotate(week=TruncWeek('created_at'))
            .values('week')
            .annotate(hires=Count('id'))
            .order_by('week')
        )

        return Response({
            'period': 'last_8_weeks',
            'data': [
                {'week': v['week'].isoformat(), 'hires': v['hires']}
                for v in velocity
            ],
        })