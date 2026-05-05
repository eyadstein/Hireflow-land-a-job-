import time
from collections import defaultdict
from django.http import JsonResponse
from django.utils import timezone
from .models import BlacklistedToken

# In-memory rate limit store (per IP)
# For production use Redis
_rate_limit_store = defaultdict(list)

RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW   = 60  # seconds


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip  = get_client_ip(request)
        now = time.time()

        # Clean old requests outside window
        _rate_limit_store[ip] = [
            t for t in _rate_limit_store[ip]
            if now - t < RATE_LIMIT_WINDOW
        ]

        if len(_rate_limit_store[ip]) >= RATE_LIMIT_REQUESTS:
            return JsonResponse({
                'error':       'Rate limit exceeded. Try again in a minute.',
                'retry_after': RATE_LIMIT_WINDOW,
            }, status=429)

        _rate_limit_store[ip].append(now)
        return self.get_response(request)


class JWTBlacklistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            if BlacklistedToken.objects.filter(token=token).exists():
                return JsonResponse(
                    {'error': 'Token has been invalidated. Please login again.'},
                    status=401
                )

        return self.get_response(request)