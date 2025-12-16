from rest_framework.views import exception_handler
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status


def handle_rest_exception_drf_helper(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, PermissionDenied) and exc.detail == 'Tu cuenta está inactiva.':
        return Response(
            {
                "status": status.HTTP_403_FORBIDDEN,
                "message": exc.detail,
                "data": None,
            },
            status=status.HTTP_403_FORBIDDEN
        )

    return response
