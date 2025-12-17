from django.core.exceptions import PermissionDenied
from rest_framework import status
from django.http import JsonResponse


# With mixins, PermissionRequiredViewMixin raise exception before calling the view and handle_rest_exception_helper handle the exception
class CustomForbiddenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # if response is 403, return custom response
        if response.status_code == status.HTTP_403_FORBIDDEN:
            response_data = {
                "status": status.HTTP_403_FORBIDDEN,
                "message": response.data.get("message") if response.data.get("message") else "Permission denied",
                "data": response.data.get("data") if response.data.get("data") else None,
            }
            return JsonResponse(
                response_data,
                status=status.HTTP_403_FORBIDDEN
            )

        return response
