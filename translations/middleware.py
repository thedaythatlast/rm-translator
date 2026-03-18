# This file was vibe coded to integrate the project to Redis for the sake of rate limiting.

from django.http import JsonResponse
from .rm_token_bucket import TokenBucket

# One shared instance - same bucket state across all requests
limiter = TokenBucket(capacity=3, refill_rate=1)

class RateLimiterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Use client IP as the rate limit key
        ip = request.META.get('REMOTE_ADDR')
        
        if not limiter.is_allowed(ip):
            return JsonResponse(
                {'error': 'Rate limit exceeded. Try again later.'},
                status=429
            )
        
        return self.get_response(request)

# 'translations.middleware.RateLimiterMiddleware'
#              ↑ filename    ↑ class name