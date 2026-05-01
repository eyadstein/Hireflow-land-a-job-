from datetime import datetime, timezone, timedelta
from .models import JobAlert, AlertMatch
from jobs_aggregator.services import aggregate_jobs
from jobs_aggregator.filters import filter_jobs


def check_alerts_for_user(user):
    """
    Check all active alerts for a user and return new matches.
    """
    alerts = JobAlert.objects.filter(
        user=user,
        is_active=True
    )

    all_new_matches = []

    for alert in alerts:
        # Check frequency
        if alert.last_triggered:
            now = datetime.now(timezone.utc)
            if alert.frequency == 'daily':
                if (now - alert.last_triggered).total_seconds() < 86400:
                    continue
            elif alert.frequency == 'weekly':
                if (now - alert.last_triggered).total_seconds() < 604800:
                    continue

        # Fetch jobs matching alert criteria
        filters = {
            'level': alert.experience_level or None,
            'job_type': alert.job_type or None,
            'salary_min': alert.salary_min,
            'remote_only': 'true' if alert.is_remote else None,
        }

        jobs = aggregate_jobs(
            query=alert.keywords,
            country=alert.country,
            include_remote=True,
            page=1,
            filters=filters
        )

        new_matches = []
        for job in jobs:
            job_id = job.get('id')
            if not job_id:
                continue

            # Check if already matched
            already_matched = AlertMatch.objects.filter(
                alert=alert,
                job_id=job_id
            ).exists()

            if not already_matched:
                match = AlertMatch.objects.create(
                    alert=alert,
                    job_id=job_id,
                    job_title=job.get('title', ''),
                    company=job.get('company', ''),
                    apply_link=job.get('apply_link'),
                )
                new_matches.append(match)

        if new_matches:
            # Update last triggered
            alert.last_triggered = datetime.now(timezone.utc)
            alert.save()
            all_new_matches.extend(new_matches)

    return all_new_matches


def get_unseen_matches(user):
    """Get all unseen alert matches for a user."""
    return AlertMatch.objects.filter(
        alert__user=user,
        is_seen=False
    ).select_related('alert').order_by('-matched_at')


def mark_matches_seen(user):
    """Mark all matches as seen."""
    AlertMatch.objects.filter(
        alert__user=user,
        is_seen=False
    ).update(is_seen=True)