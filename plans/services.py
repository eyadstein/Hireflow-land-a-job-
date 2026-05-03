from django.utils import timezone
from .models import UsageTracker, PlanLimit


# Define limits directly in code as fallback
PLAN_LIMITS = {
    'free': {
        'ai_uses_per_day': 5,
        'saved_jobs_limit': 10,
        'alerts_limit': 2,
        'can_see_salary': False,
        'can_use_interview_coach': False,
        'can_use_cv_builder': False,
    },
    'pro': {
        'ai_uses_per_day': 999,
        'saved_jobs_limit': 999,
        'alerts_limit': 20,
        'can_see_salary': True,
        'can_use_interview_coach': True,
        'can_use_cv_builder': True,
    }
}


def get_plan_limits(plan):
    """Get limits for a plan."""
    return PLAN_LIMITS.get(plan, PLAN_LIMITS['free'])


def get_today_usage(user, feature):
    """Get usage count for today."""
    today = timezone.now().date()
    tracker, _ = UsageTracker.objects.get_or_create(
        user=user,
        feature=feature,
        date=today,
        defaults={'count': 0}
    )
    return tracker.count


def increment_usage(user, feature):
    """Increment usage count for today."""
    today = timezone.now().date()
    tracker, _ = UsageTracker.objects.get_or_create(
        user=user,
        feature=feature,
        date=today,
        defaults={'count': 0}
    )
    tracker.count += 1
    tracker.save()
    return tracker.count


def can_use_feature(user, feature):
    """
    Check if user can use a feature based on their plan.
    Returns (allowed, reason, remaining)
    """
    plan = user.plan
    limits = get_plan_limits(plan)

    # Check feature-specific limits
    if feature == 'ai':
        daily_limit = limits['ai_uses_per_day']
        today_usage = get_today_usage(user, 'ai')
        if today_usage >= daily_limit:
            return False, f"Daily limit reached ({daily_limit} uses/day on free plan). Upgrade to Pro for unlimited access.", 0
        return True, "OK", daily_limit - today_usage

    elif feature == 'salary':
        if not limits['can_see_salary']:
            return False, "Salary insights are a Pro feature. Upgrade to unlock.", 0
        return True, "OK", -1

    elif feature == 'interview_coach':
        if not limits['can_use_interview_coach']:
            return False, "Interview coach is a Pro feature. Upgrade to unlock.", 0
        return True, "OK", -1

    elif feature == 'cv_builder':
        if not limits['can_use_cv_builder']:
            return False, "CV builder is a Pro feature. Upgrade to unlock.", 0
        return True, "OK", -1

    elif feature == 'saved_jobs':
        from jobs.models import SavedJob
        saved_count = SavedJob.objects.filter(user=user).count()
        limit = limits['saved_jobs_limit']
        if saved_count >= limit:
            return False, f"Saved jobs limit reached ({limit} on free plan). Upgrade to Pro for unlimited.", 0
        return True, "OK", limit - saved_count

    elif feature == 'alerts':
        from jobs.models import JobAlert
        alerts_count = JobAlert.objects.filter(user=user, is_active=True).count()
        limit = limits['alerts_limit']
        if alerts_count >= limit:
            return False, f"Alerts limit reached ({limit} on free plan). Upgrade to Pro for more.", 0
        return True, "OK", limit - alerts_count

    return True, "OK", -1


def get_user_plan_status(user):
    """Get full plan status for a user."""
    plan = user.plan
    limits = get_plan_limits(plan)
    today_ai_usage = get_today_usage(user, 'ai')

    from jobs.models import SavedJob, JobAlert
    saved_count = SavedJob.objects.filter(user=user).count()
    alerts_count = JobAlert.objects.filter(user=user, is_active=True).count()

    return {
        'plan': plan,
        'is_pro': plan == 'pro',
        'limits': limits,
        'usage': {
            'ai_today': today_ai_usage,
            'ai_remaining': max(0, limits['ai_uses_per_day'] - today_ai_usage),
            'saved_jobs': saved_count,
            'saved_jobs_remaining': max(0, limits['saved_jobs_limit'] - saved_count),
            'active_alerts': alerts_count,
            'alerts_remaining': max(0, limits['alerts_limit'] - alerts_count),
        },
        'features': {
            'salary_insights': limits['can_see_salary'],
            'interview_coach': limits['can_use_interview_coach'],
            'cv_builder': limits['can_use_cv_builder'],
        }
    }