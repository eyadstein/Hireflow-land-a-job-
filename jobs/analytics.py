from django.db.models import Count
from django.db.models.functions import TruncWeek
from django.utils import timezone
from datetime import timedelta
from applications.models import Application


def last_30_days():
    return timezone.now() - timedelta(days=30)


def get_seeker_stats(user):
    apps = Application.objects.filter(user=user)

    total = apps.count()

    status_breakdown = {
        item['status']: item['count']
        for item in apps.values('status').annotate(count=Count('id'))
    }
    for s, _ in Application.KANBAN_STATUS_CHOICES:
        status_breakdown.setdefault(s, 0)

    recent = (
        apps.filter(created_at__gte=last_30_days())
        .annotate(week=TruncWeek('created_at'))
        .values('week')
        .annotate(count=Count('id'))
        .order_by('week')
    )
    weekly_activity = [
        {
            'week':  item['week'].strftime('%Y-%m-%d'),
            'count': item['count'],
        }
        for item in recent
    ]

    top_companies = (
        apps.exclude(job=None)
        .values('job__company')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )
    manual_companies = (
        apps.filter(job=None)
        .exclude(company_name='')
        .values('company_name')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )

    companies = [
        {'company': item['job__company'], 'count': item['count']}
        for item in top_companies
    ] + [
        {'company': item['company_name'], 'count': item['count']}
        for item in manual_companies
    ]
    companies = sorted(companies, key=lambda x: x['count'], reverse=True)[:5]

    return {
        'total_applications': total,
        'status_breakdown':   status_breakdown,
        'weekly_activity':    weekly_activity,
        'top_companies':      companies,
    }


def get_recruiter_stats(user):
    from jobs.models import Job

    jobs               = Job.objects.filter(posted_by=user)
    total_jobs         = jobs.count()
    total_applications = Application.objects.filter(job__in=jobs).count()

    per_job = (
        jobs.annotate(app_count=Count('tracker_entries'))
        .values('id', 'title', 'company', 'app_count')
        .order_by('-app_count')
    )
    applications_per_job = [
        {
            'job_id':    item['id'],
            'job_title': item['title'],
            'company':   item['company'],
            'applicants': item['app_count'],
        }
        for item in per_job
    ]

    recent_applicants = (
        Application.objects.filter(job__in=jobs)
        .select_related('user', 'job')
        .order_by('-created_at')[:10]
    )
    recent = [
        {
            'applicant':  app.user.username,
            'job_title':  app.job.title,
            'company':    app.job.company,
            'status':     app.status,
            'applied_at': app.created_at.strftime('%Y-%m-%d'),
        }
        for app in recent_applicants
    ]

    return {
        'total_jobs_posted':    total_jobs,
        'total_applications':   total_applications,
        'applications_per_job': applications_per_job,
        'recent_applicants':    recent,
    }