from django.http import JsonResponse
from rest_framework import status


class CustomUnauthorizedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # if response is 401, return custom response
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            response_data = {
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": response.data.get("message") if response.data.get("message") else "Authentication credentials were not provided.",
                "data": response.data.get("data") if response.data.get("data") else None,
            }
            return JsonResponse(response_data, status=status.HTTP_401_UNAUTHORIZED)

        return response
