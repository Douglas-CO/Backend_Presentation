from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.exceptions import NotAuthenticated
from rest_framework import status
from django.core.exceptions import ValidationError
from django.core.exceptions import PermissionDenied
from django.core.exceptions import FieldError
from django.db import IntegrityError

import traceback


from config.shared.serializers.serializers import (
    ErrorResponseDTO,
    NotFoundErrorResponseDTO,
    UnauthorizedErrorResponseDTO,
)
from config.shared.exceptions.resource_not_found_exception import (
    ResourceNotFoundException,
)
from config.shared.exceptions.invalid_fields_exception import InvalidFieldsException
from config.shared.exceptions.unauthorized_exception import UnauthorizedException
from config.shared.exceptions.bad_request_exception import BadRequestException
from config.shared.exceptions.conflicts_exception import ConflictsException
from config.shared.exceptions.locked_request_exception import LockedRequestException
from config.shared.exceptions.custom_generic_exception import CustomGenericException
from config.shared.exceptions.custom_netconnect_exception import CustomNetConnectException

from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.exceptions import PermissionDenied as PermissionDeniedDRF


def handle_rest_exception_helper(exc):

    if isinstance(exc, NotAuthenticated) or isinstance(exc, UnauthorizedException):
        error = UnauthorizedErrorResponseDTO(
            status=status.HTTP_401_UNAUTHORIZED, message=str(exc), data=exc.data if hasattr(exc, 'data') else None
        )
        return Response(error.__dict__, status=status.HTTP_401_UNAUTHORIZED)
    elif isinstance(exc, Token.DoesNotExist) or isinstance(exc, AuthenticationFailed):
        error = UnauthorizedErrorResponseDTO(
            status=status.HTTP_401_UNAUTHORIZED, message=str(exc)
        )
        return Response(error.__dict__, status=status.HTTP_401_UNAUTHORIZED)
    elif isinstance(exc, PermissionDenied) or isinstance(exc, PermissionDeniedDRF):
        error = UnauthorizedErrorResponseDTO(
            status=status.HTTP_403_FORBIDDEN, message='Permission denied'
        )
        return Response(error.__dict__, status=status.HTTP_403_FORBIDDEN)

    if isinstance(exc, IntegrityError):
        return Response(
            {
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error de integridad de datos",
                "details": str(exc),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(exc, ResourceNotFoundException):
        not_found = NotFoundErrorResponseDTO(
            status=status.HTTP_404_NOT_FOUND,
            message=str(exc),
        )
        # JsonResponse 'cause own 404 middleware
        return JsonResponse(not_found.__dict__, status=status.HTTP_404_NOT_FOUND)
    elif isinstance(exc, CustomGenericException):
        custom_error = ErrorResponseDTO(
            status=exc.status,
            message=str(exc),
            data=exc.data,
        )
        return Response(custom_error.__dict__, status=exc.status)
    elif isinstance(exc, CustomNetConnectException):
        custom_error = ErrorResponseDTO(
            status=exc.status,
            message=str(exc),
            data=exc.data,
        )
        return Response(custom_error.__dict__, status=exc.status)
    elif isinstance(exc, LockedRequestException):
        locked_request = ErrorResponseDTO(
            status=status.HTTP_423_LOCKED,
            message=str(exc),
        )
        return Response(locked_request.__dict__, status=status.HTTP_423_LOCKED)
    elif isinstance(exc, InvalidFieldsException):
        invalid_fields = [
            f"{field}: {error}" for field, errors in exc.fields for error in errors
        ]
        bad_request = ErrorResponseDTO(
            status=status.HTTP_400_BAD_REQUEST,
            message=str(exc),
            invalid_fields=invalid_fields,
        )
        return Response(bad_request.__dict__, status=status.HTTP_400_BAD_REQUEST)
    elif isinstance(exc, BadRequestException):
        bad_request = ErrorResponseDTO(
            status=status.HTTP_400_BAD_REQUEST,
            message=str(exc),
            data=exc.data,
        )
        return Response(bad_request.__dict__, status=status.HTTP_400_BAD_REQUEST)
    elif isinstance(exc, FieldError):  # handle order_by field error
        bad_request = ErrorResponseDTO(
            status=status.HTTP_400_BAD_REQUEST,
            message='Invalid filter field',
        )
        return Response(bad_request.__dict__, status=status.HTTP_400_BAD_REQUEST)
    elif isinstance(exc, ConflictsException):
        conflict = ErrorResponseDTO(
            status=status.HTTP_409_CONFLICT,
            message=str(exc),
            data=exc.data,
        )
        return Response(conflict.__dict__, status=status.HTTP_409_CONFLICT)
    # does not override the DRF serializer errors response
    elif isinstance(exc, ValidationError):
        validation_error = ErrorResponseDTO(
            status=status.HTTP_400_BAD_REQUEST,
            message="Invalid fields",
            invalid_fields=exc.messages
        )
        return Response(validation_error.__dict__, status=status.HTTP_400_BAD_REQUEST)
    else:
        print('--------- UNEXPECTED ERROR ---------')
        print(traceback.format_exc())
        error = ErrorResponseDTO(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=str(exc),
        )
        return Response(error.__dict__, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
