from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import models as db_models
from django.db.models import Count, Q
from django.db.models.functions import TruncDate, TruncWeek, ExtractHour, ExtractWeekDay
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


# ── Recruiter Performance Analytics endpoints ──

class PerformanceSummaryView(APIView):
    """GET overall performance metrics for the recruiter."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        my_jobs = Job.objects.filter(posted_by=request.user)
        my_job_ids = my_jobs.values_list('id', flat=True)
        apps = Application.objects.filter(job_id__in=my_job_ids)

        total_apps = apps.count()
        reviewed_apps = apps.exclude(status='pending')
        reviewed_count = reviewed_apps.count()
        pending_count = apps.filter(status='pending').count()

        review_rate = round((reviewed_count / total_apps) * 100) if total_apps > 0 else 0

        apps_with_review = apps.filter(reviewed_at__isnull=False)
        if apps_with_review.exists():
            total_hours = 0
            count = 0
            for app in apps_with_review:
                diff = app.reviewed_at - app.created_at
                total_hours += diff.total_seconds() / 3600
                count += 1
            avg_response_hours = round(total_hours / count, 1) if count > 0 else 0
        else:
            avg_response_hours = 0

        speed_score = max(0, min(100, 100 - (avg_response_hours * 1.5))) if avg_response_hours > 0 else 50
        efficiency_score = round((review_rate * 0.6) + (speed_score * 0.4))

        accepted = apps.filter(status='accepted').count()
        rejected = apps.filter(status='rejected').count()
        decided = accepted + rejected
        acceptance_rate = round((accepted / decided) * 100) if decided > 0 else 0

        return Response({
            'total_jobs_posted': my_jobs.count(),
            'total_applications': total_apps,
            'reviewed': reviewed_count,
            'pending': pending_count,
            'review_rate': review_rate,
            'avg_response_hours': avg_response_hours,
            'efficiency_score': efficiency_score,
            'acceptance_rate': acceptance_rate,
        })


class ActivityLogView(APIView):
    """GET daily activity for the last 30 days."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        my_job_ids = Job.objects.filter(
            posted_by=request.user
        ).values_list('id', flat=True)

        thirty_days_ago = timezone.now() - timedelta(days=30)

        jobs_per_day = (
            Job.objects.filter(
                posted_by=request.user,
                created_at__gte=thirty_days_ago
            )
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(jobs_posted=Count('id'))
            .order_by('date')
        )

        reviews_per_day = (
            Application.objects.filter(
                job_id__in=my_job_ids,
                reviewed_at__isnull=False,
                reviewed_at__gte=thirty_days_ago
            )
            .annotate(date=TruncDate('reviewed_at'))
            .values('date')
            .annotate(
                reviews=Count('id'),
                accepts=Count('id', filter=db_models.Q(status='accepted')),
                rejects=Count('id', filter=db_models.Q(status='rejected'))
            )
            .order_by('date')
        )

        activity = {}

        for entry in jobs_per_day:
            d = entry['date'].isoformat()
            activity[d] = {'date': d, 'jobs_posted': entry['jobs_posted'], 'reviews': 0, 'accepts': 0, 'rejects': 0}

        for entry in reviews_per_day:
            d = entry['date'].isoformat()
            if d in activity:
                activity[d]['reviews'] = entry['reviews']
                activity[d]['accepts'] = entry['accepts']
                activity[d]['rejects'] = entry['rejects']
            else:
                activity[d] = {'date': d, 'jobs_posted': 0, 'reviews': entry['reviews'], 'accepts': entry['accepts'], 'rejects': entry['rejects']}

        sorted_activity = sorted(activity.values(), key=lambda x: x['date'])

        return Response({
            'period': 'last_30_days',
            'data': sorted_activity,
        })


class DecisionPatternsView(APIView):
    """GET weekly accept vs reject ratio over last 8 weeks."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        my_job_ids = Job.objects.filter(
            posted_by=request.user
        ).values_list('id', flat=True)

        eight_weeks_ago = timezone.now() - timedelta(weeks=8)

        weekly = (
            Application.objects.filter(
                job_id__in=my_job_ids,
                reviewed_at__isnull=False,
                reviewed_at__gte=eight_weeks_ago
            )
            .annotate(week=TruncWeek('reviewed_at'))
            .values('week')
            .annotate(
                total_decisions=Count('id'),
                accepted=Count('id', filter=db_models.Q(status='accepted')),
                rejected=Count('id', filter=db_models.Q(status='rejected'))
            )
            .order_by('week')
        )

        return Response({
            'period': 'last_8_weeks',
            'data': [
                {
                    'week': w['week'].isoformat(),
                    'total_decisions': w['total_decisions'],
                    'accepted': w['accepted'],
                    'rejected': w['rejected'],
                    'accept_ratio': round((w['accepted'] / w['total_decisions']) * 100) if w['total_decisions'] > 0 else 0,
                }
                for w in weekly
            ],
        })


class BusiestPeriodsView(APIView):
    """GET which days of week and hours have most recruiter activity."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        my_job_ids = Job.objects.filter(
            posted_by=request.user
        ).values_list('id', flat=True)

        reviewed_apps = Application.objects.filter(
            job_id__in=my_job_ids,
            reviewed_at__isnull=False
        )

        day_names = {1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday', 5: 'Thursday', 6: 'Friday', 7: 'Saturday'}

        by_day = (
            reviewed_apps
            .annotate(day=ExtractWeekDay('reviewed_at'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        by_hour = (
            reviewed_apps
            .annotate(hour=ExtractHour('reviewed_at'))
            .values('hour')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        return Response({
            'busiest_days': [
                {
                    'day': day_names.get(d['day'], f"Day {d['day']}"),
                    'reviews': d['count'],
                }
                for d in by_day
            ],
            'busiest_hours': [
                {
                    'hour': f"{h['hour']:02d}:00",
                    'reviews': h['count'],
                }
                for h in by_hour[:5]
            ],
        })


class ResponseTimesView(APIView):
    """GET average response time per job."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        my_jobs = Job.objects.filter(posted_by=request.user)

        result = []
        for job in my_jobs:
            reviewed = Application.objects.filter(
                job=job,
                reviewed_at__isnull=False
            )
            if reviewed.exists():
                total_hours = 0
                count = 0
                for app in reviewed:
                    diff = app.reviewed_at - app.created_at
                    total_hours += diff.total_seconds() / 3600
                    count += 1
                avg_hours = round(total_hours / count, 1) if count > 0 else 0
            else:
                avg_hours = None

            pending = Application.objects.filter(job=job, status='pending').count()
            total = Application.objects.filter(job=job).count()

            result.append({
                'job_id': job.id,
                'title': job.title,
                'company': job.company,
                'total_applications': total,
                'pending': pending,
                'avg_response_hours': avg_hours,
            })

        return Response({
            'jobs': sorted(result, key=lambda x: x['total_applications'], reverse=True),
        })
