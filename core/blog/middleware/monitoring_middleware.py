import time
import requests

from django.conf import settings


class MonitoringMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time

        self.monitor_performance(request, response, duration)

        return response

    def monitor_performance(self, request, response, duration):
        payload = {
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "response_time": duration,
            "timestamp": time.time(),
        }
        response = requests.post(settings.MONITORING_SERVER, json=payload)

        if response.status_code != 200:
            print(response.status_code)
