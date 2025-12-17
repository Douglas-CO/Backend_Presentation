import json
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status


class FrontVersionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        front_version = request.headers.get('X-Front-Version')
        request_path = request.path

        # conditions to skip the middleware to refresh system params -------
        if not front_version or request_path == '/api/v1/parametrosistema/':
            return None

        return None
