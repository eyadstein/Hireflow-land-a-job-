from django.http import JsonResponse
from .services import can_use_feature, increment_usage

# Map URL paths to features
FEATURE_MAP = {
    '/api/ai/resume/': 'ai',
    '/api/ai/cover-letter/': 'ai',
    '/api/ai/interview/': 'interview_coach',
    '/api/ai/salary/': 'salary',
    '/api/ai/agent/': 'ai',
    '/api/jobs/saved/toggle/': 'saved_jobs',
    '/api/jobs/alerts/': 'alerts',
}


class PlanLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only check POST requests on protected endpoints
        if request.method == 'POST' and request.user.is_authenticated:
            path = request.path
            feature = FEATURE_MAP.get(path)

            if feature:
                allowed, reason, remaining = can_use_feature(
                    request.user,
                    feature
                )
                if not allowed:
                    return JsonResponse({
                        'error': 'plan_limit_reached',
                        'message': reason,
                        'upgrade_url': '/api/plans/upgrade/',
                    }, status=403)

                # Increment usage for AI features
                if feature == 'ai':
                    increment_usage(request.user, 'ai')

        response = self.get_response(request)
        return response