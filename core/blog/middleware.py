import logging
import time

import requests
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse, HttpResponsePermanentRedirect

logger = logging.getLogger(__name__)


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(f"Request: {request.method} {request.path}")

        response = self.get_response(request)

        logger.info(f"Response: {response.status_code} {response.reason_phrase}")

        return response


class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("Before view")

        response = self.get_response(request)

        print("After view")

        return response


class TokenAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.headers.get("Authorization")
        if (
            token
            != "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6Ikl0J3MgZG9lbid0IG15IHRva2VuIGxvbCIsImlhdCI6MTUxNjIzOTAyMn0.HE38TsD6eb5A4FgecBFjCfUW2QnOblpnZ44TIVWvrZE"
        ):
            return JsonResponse({"error": "Invalid token"}, status=401)

        response = self.get_response(request)

        return response


class CustomHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        response["X-Custom-Header"] = "My Custom Header Value"

        return response


class TimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time
        response["X-Request-Duration"] = str(duration)

        return response


class ExceptionHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        return response


class CacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "GET":
            cache_key = f"cache_{request.get_full_path()}"
            response = cache.get(cache_key)
            if response:
                return response

            response = self.get_response(request)
            cache.set(cache_key, response, timeout=60 * 15)
            return response

        return self.get_response(request)


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META["REMOTE_ADDR"]
        cache_key = f"rate_limit_{ip}"
        requests = cache.get(cache_key, 0)

        if request >= 100:
            return JsonResponse({"error": "Too many requests"}, status=429)

        cache.set(cache_key, requests + 1, timeout=60 * 60)

        response = self.get_response(request)

        return response


class SSLRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.is_secure():
            url = request.build_absolute_uri(request.get_full_path())
            secure_url = url.replace("http://", "https://")
            return HttpResponsePermanentRedirect(secure_url)

        return self.get_response(request)


class ComplexMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(f"Request: {request.method} {request.path}")

        ip = request.META["REMOTE_ADDR"]
        cache_key = f"rate_limit_{ip}"
        requests_count = cache.get(cache_key, 0)

        if requests_count >= 100:
            self.notify_excessive_requests(ip)
            return JsonResponse({"error": "Too Many Requests"}, status=429)

        cache.set(cache_key, requests_count + 1, timeout=60 * 60)

        if request.method == "GET":
            cache_key = f"cache_{request.get_full_path()}"
            cached_response = cache.get(cache_key)
            if cached_response:
                return cached_response

        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time
        response["X-Request-Duration"] = str(duration)

        logger.info(f"Response: {response.status_code} {response.reason_phrase}")

        if request.method == "GET" and response.status_code == 200:
            cache.set(cache_key, response, timeout=60 * 15)

        return response

    def notify_excessive_requests(self, ip):
        payload = {"ip": ip, "message": "Too many requests from this IP"}
        response = requests.post(settings.NOTIFY_URL, json=payload)
        if response.status_code != 200:
            logger.info(f"Notification sent for IP: {ip}")
        else:
            logger.error(f"Failed to send notification for IP: {ip}")
