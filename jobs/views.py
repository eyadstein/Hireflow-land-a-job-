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


# ── Top Candidate Identification endpoints ──

def calculate_candidate_score(applicant, job, application):
    score = 0

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

    all_apps = Application.objects.filter(applicant=applicant)
    total_decided = all_apps.filter(status__in=['accepted', 'rejected']).count()
    accepted = all_apps.filter(status='accepted').count()
    if total_decided > 0:
        past_rate = accepted / total_decided
        score += round(past_rate * 25)
    else:
        score += 10

    total_applications = all_apps.count()
    if total_applications >= 5:
        score += 20
    elif total_applications >= 3:
        score += 15
    elif total_applications >= 2:
        score += 10
    else:
        score += 5

    completeness = 0
    if applicant.email:
        completeness += 5
    if applicant.first_name:
        completeness += 5
    if applicant.last_name:
        completeness += 5
    score += completeness

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

        candidates.sort(key=lambda x: x['score'], reverse=True)

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


# ── Job Performance Optimization endpoints ──

def analyze_job_health(job):
    score = 0
    suggestions = []
    field_status = {}

    if job.title:
        title_len = len(job.title)
        if title_len >= 10:
            score += 10
            field_status['title'] = 'good'
        elif title_len >= 5:
            score += 6
            field_status['title'] = 'weak'
            suggestions.append('Make the job title more descriptive (aim for 10+ characters).')
        else:
            score += 2
            field_status['title'] = 'poor'
            suggestions.append('Job title is too short. Use a clear, specific title like "Senior Backend Developer".')
    else:
        field_status['title'] = 'missing'
        suggestions.append('Add a job title.')

    if job.company and len(job.company) >= 2:
        score += 5
        field_status['company'] = 'good'
    else:
        field_status['company'] = 'missing'
        suggestions.append('Add a company name.')

    if job.description:
        desc_len = len(job.description)
        if desc_len >= 200:
            score += 20
            field_status['description'] = 'good'
        elif desc_len >= 100:
            score += 14
            field_status['description'] = 'weak'
            suggestions.append('Expand the job description to at least 200 characters. Include responsibilities and expectations.')
        elif desc_len >= 30:
            score += 8
            field_status['description'] = 'poor'
            suggestions.append('Job description is too short. Add detailed responsibilities, team info, and what the role involves.')
        else:
            score += 3
            field_status['description'] = 'poor'
            suggestions.append('Job description needs significant improvement. Aim for 200+ characters with clear role details.')
    else:
        field_status['description'] = 'missing'
        suggestions.append('Add a job description — this is the most important field for attracting candidates.')

    if job.location and len(job.location) >= 3:
        score += 5
        field_status['location'] = 'good'
    else:
        field_status['location'] = 'missing'
        suggestions.append('Add a location. Candidates filter by location — missing it reduces visibility.')

    if job.salary and len(job.salary) >= 3:
        score += 15
        field_status['salary'] = 'good'
    else:
        score += 0
        field_status['salary'] = 'missing'
        suggestions.append('Add salary information. Job postings with salary get 30% more applications.')

    if hasattr(job, 'job_type') and job.job_type:
        score += 5
        field_status['job_type'] = 'good'
    else:
        field_status['job_type'] = 'missing'
        suggestions.append('Specify the job type (Remote, On-site, or Hybrid).')

    if hasattr(job, 'career_level') and job.career_level:
        score += 5
        field_status['career_level'] = 'good'
    else:
        field_status['career_level'] = 'missing'
        suggestions.append('Add a career level (Entry, Mid, Senior, etc.) to attract the right candidates.')

    if hasattr(job, 'requirements') and job.requirements and len(job.requirements) >= 20:
        score += 10
        field_status['requirements'] = 'good'
    elif hasattr(job, 'requirements') and job.requirements:
        score += 5
        field_status['requirements'] = 'weak'
        suggestions.append('Expand the requirements section. List specific skills and qualifications needed.')
    else:
        field_status['requirements'] = 'missing'
        suggestions.append('Add job requirements — candidates need to know if they qualify.')

    if hasattr(job, 'education') and job.education:
        score += 5
        field_status['education'] = 'good'
    else:
        field_status['education'] = 'missing'
        suggestions.append("Specify education requirements (e.g., \"Bachelor's in CS\").")

    if hasattr(job, 'years_experience') and job.years_experience:
        score += 5
        field_status['years_experience'] = 'good'
    else:
        field_status['years_experience'] = 'missing'
        suggestions.append('Add years of experience required (e.g., "2-4 years").')

    app_count = Application.objects.filter(job=job).count()
    days_posted = (timezone.now() - job.created_at).days + 1
    apps_per_day = app_count / days_posted if days_posted > 0 else 0

    if app_count >= 10:
        score += 15
        field_status['application_rate'] = 'excellent'
    elif app_count >= 5:
        score += 10
        field_status['application_rate'] = 'good'
    elif app_count >= 1:
        score += 5
        field_status['application_rate'] = 'low'
        suggestions.append(f'Only {app_count} application(s) received. Consider improving the description or adding salary info.')
    else:
        score += 0
        field_status['application_rate'] = 'none'
        suggestions.append('No applications yet. Review the suggestions above and repost with improvements.')

    if score >= 85:
        grade = 'A'
        status_label = 'Excellent'
    elif score >= 70:
        grade = 'B'
        status_label = 'Good'
    elif score >= 50:
        grade = 'C'
        status_label = 'Needs improvement'
    elif score >= 30:
        grade = 'D'
        status_label = 'Poor'
    else:
        grade = 'F'
        status_label = 'Critical'

    good_fields = sum(1 for v in field_status.values() if v in ('good', 'excellent'))
    total_fields = len(field_status)
    completeness = round((good_fields / total_fields) * 100) if total_fields > 0 else 0

    return {
        'health_score': min(score, 100),
        'grade': grade,
        'status': status_label,
        'completeness': completeness,
        'fields': field_status,
        'suggestions': suggestions,
        'metrics': {
            'total_applications': app_count,
            'days_posted': days_posted,
            'applications_per_day': round(apps_per_day, 2),
        },
    }


class JobOptimizeView(APIView):
    """GET health score and optimization suggestions for a specific job."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, job_id):
        job = Job.objects.filter(id=job_id, posted_by=request.user).first()
        if not job:
            return Response({'error': 'Job not found or not owned by you.'}, status=404)

        analysis = analyze_job_health(job)

        return Response({
            'job_id': job.id,
            'title': job.title,
            'company': job.company,
            'created_at': job.created_at.isoformat(),
            **analysis,
        })


class OptimizationReportView(APIView):
    """GET optimization overview for ALL of the recruiter's jobs."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        my_jobs = Job.objects.filter(posted_by=request.user).order_by('-created_at')

        jobs_report = []
        total_score = 0
        critical_jobs = []
        excellent_jobs = []

        for job in my_jobs:
            analysis = analyze_job_health(job)
            total_score += analysis['health_score']

            job_summary = {
                'job_id': job.id,
                'title': job.title,
                'company': job.company,
                'health_score': analysis['health_score'],
                'grade': analysis['grade'],
                'status': analysis['status'],
                'completeness': analysis['completeness'],
                'suggestions_count': len(analysis['suggestions']),
                'applications': analysis['metrics']['total_applications'],
                'days_posted': analysis['metrics']['days_posted'],
            }

            jobs_report.append(job_summary)

            if analysis['grade'] in ['D', 'F']:
                critical_jobs.append(job_summary)
            elif analysis['grade'] == 'A':
                excellent_jobs.append(job_summary)

        avg_score = round(total_score / my_jobs.count()) if my_jobs.count() > 0 else 0

        return Response({
            'total_jobs': my_jobs.count(),
            'average_health_score': avg_score,
            'critical_jobs_count': len(critical_jobs),
            'excellent_jobs_count': len(excellent_jobs),
            'jobs': jobs_report,
            'critical_jobs': critical_jobs,
            'top_suggestion': 'Add salary information to all jobs — it increases applications by 30%.' if any(
                j['completeness'] < 80 for j in jobs_report
            ) else 'Your job postings are well optimized!',
        })
