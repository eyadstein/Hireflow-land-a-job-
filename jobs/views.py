from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
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


# ── Job Performance Optimization (Omar — #43) ──

def analyze_job_health(job):
    """
    Analyze a job posting and return a health score (0-100)
    with specific suggestions for improvement.
    """
    score = 0
    suggestions = []
    field_status = {}

    # 1. Title quality (max 10)
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

    # 2. Company name (max 5)
    if job.company and len(job.company) >= 2:
        score += 5
        field_status['company'] = 'good'
    else:
        field_status['company'] = 'missing'
        suggestions.append('Add a company name.')

    # 3. Description quality (max 20)
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

    # 4. Location (max 5)
    if job.location and len(job.location) >= 3:
        score += 5
        field_status['location'] = 'good'
    else:
        field_status['location'] = 'missing'
        suggestions.append('Add a location. Candidates filter by location — missing it reduces visibility.')

    # 5. Salary (max 15)
    if job.salary and len(job.salary) >= 3:
        score += 15
        field_status['salary'] = 'good'
    else:
        score += 0
        field_status['salary'] = 'missing'
        suggestions.append('Add salary information. Job postings with salary get 30% more applications.')

    # 6. Job type (max 5)
    if hasattr(job, 'job_type') and job.job_type:
        score += 5
        field_status['job_type'] = 'good'
    else:
        field_status['job_type'] = 'missing'
        suggestions.append('Specify the job type (Remote, On-site, or Hybrid).')

    # 7. Career level (max 5)
    if hasattr(job, 'career_level') and job.career_level:
        score += 5
        field_status['career_level'] = 'good'
    else:
        field_status['career_level'] = 'missing'
        suggestions.append('Add a career level (Entry, Mid, Senior, etc.) to attract the right candidates.')

    # 8. Requirements (max 10)
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

    # 9. Education (max 5)
    if hasattr(job, 'education') and job.education:
        score += 5
        field_status['education'] = 'good'
    else:
        field_status['education'] = 'missing'
        suggestions.append('Specify education requirements (e.g., "Bachelor\'s in CS").')

    # 10. Experience (max 5)
    if hasattr(job, 'years_experience') and job.years_experience:
        score += 5
        field_status['years_experience'] = 'good'
    else:
        field_status['years_experience'] = 'missing'
        suggestions.append('Add years of experience required (e.g., "2-4 years").')

    # 11. Application performance (max 15)
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

    # Determine health grade
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

    # Count field statuses
    good_fields = sum(1 for v in field_status.values() if v == 'good' or v == 'excellent')
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