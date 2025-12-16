from rest_framework.decorators import api_view

# ### Authentication & Authorization
from rest_framework.authentication import TokenAuthentication  # permissions
from rest_framework.permissions import IsAuthenticated  # authentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from rest_framework.permissions import IsAdminUser

# ### docs openapi
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework import status
from rest_framework.response import Response

from config.shared.di.di import container
from config.shared.serializers.serializers import (
    BadRequestSerializer,
)
from users.services.auth_service import AuthService
from users.serializers.auth_serializers import LoginSerializer, PermissionListQueryDocWrapperSerializer, LoginResponseDocWrapperSerializer
from users.serializers.user_serializers import UserOptDocSerializer
from config.shared.helpers.handle_rest_exception_helper import (
    handle_rest_exception_helper,
)

from config.shared.constants.constants import page_size_openapi, page_openapi
from config.shared.helpers.pagination_helper import get_pagination_parameters_rest
from config.shared.helpers.request_netinfo import get_request_netinfo


class AuthView(APIView):
    service = AuthService

    # constructor: DI
    def __init__(self):
        self.service = container.auth_service()

    @swagger_auto_schema(
        operation_description="User Login",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response("OK", LoginResponseDocWrapperSerializer),
            400: openapi.Response("Bad Request", BadRequestSerializer),
            401: openapi.Response(
                "Unauthorized",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "data": openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                            "failed_attempts": openapi.Schema(type=openapi.TYPE_INTEGER, description="Failed login attempts"),
                        }),
                    },
                )
            ),
            409: openapi.Response(
                "Session already exists for this user.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "data": openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                            "ip": openapi.Schema(type=openapi.TYPE_STRING),
                            "os": openapi.Schema(type=openapi.TYPE_STRING),
                        }),
                    },
                )
            ),
        },
    )
    def post(self, request):
        try:
            net = get_request_netinfo(request)
            ip = net["client_ip"]
            os = net["user_agent"]

            serialized_instance = self.service.login(
                data=request.data, ip=ip, os=os, request=request)

            return Response({
                "status": status.HTTP_200_OK,
                "message": "Inicio de sesión exitoso",
                "data": serialized_instance,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return self.handle_exception(e)

    def handle_exception(self, exc):
        return handle_rest_exception_helper(exc)


# ### Logout in this way 'case avoid class-based issues with auth and permissions in logout
# auth and permissions
@swagger_auto_schema(
    method="post",
    operation_description="User Logout",
    responses={
        200: openapi.Response("OK", openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "status": openapi.Schema(type=openapi.TYPE_INTEGER),
                "message": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ))
    },
)
@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        request.user.auth_token.delete()
        return Response({
            "status": status.HTTP_200_OK,
            "message": "Sesión cerrada exitosamente.",
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "status": "error",
            "message": "Ocurrió un error al cerrar la sesión.",
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ### Authorization


@swagger_auto_schema(
    method="get",
    operation_description="Get permission list",
    manual_parameters=[
        openapi.Parameter('user_id', openapi.IN_QUERY,
                          description="User ID to get permissions", type=openapi.TYPE_INTEGER),
        openapi.Parameter('group_id', openapi.IN_QUERY,
                          description="Group ID to get permissions", type=openapi.TYPE_INTEGER),
        page_openapi,
        page_size_openapi,
    ],
    responses={
        200: openapi.Response("OK", PermissionListQueryDocWrapperSerializer),
        401: openapi.Response("Unauthorized", openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "status": openapi.Schema(type=openapi.TYPE_INTEGER),
                "message": openapi.Schema(type=openapi.TYPE_STRING),
            },
        )),
    },
)
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])  # is_staff - not is_superuser
def get_permissions(request):
    try:
        auth_service = container.auth_service()
        _, page_number, page_size = get_pagination_parameters_rest(
            request)

        if 'user_id' in request.query_params:
            permissions_list = auth_service.get_user_permissions(
                user_id=request.query_params.get('user_id'), page_number=page_number, page_size=page_size)
            return Response({
                "status": status.HTTP_200_OK,
                "message": "Permisos obtenidos exitosamente",
                "data": {
                    "meta": permissions_list['meta'],
                    "items": permissions_list['data'],
                }
            }, status=status.HTTP_200_OK)
        if 'group_id' in request.query_params:
            permissions_list = auth_service.get_group_permissions(
                group_id=request.query_params.get('group_id'), page_number=page_number, page_size=page_size)
            return Response({
                "status": status.HTTP_200_OK,
                "message": "Permisos obtenidos exitosamente",
                "data": {
                    "meta": permissions_list['meta'],
                    "items": permissions_list['data'],
                }
            }, status=status.HTTP_200_OK)

        all_permissions = auth_service.find_all_permissions(
            page_number=page_number, page_size=page_size)
        return Response({
            "status": status.HTTP_200_OK,
            "message": "Permisos obtenidos exitosamente",
            "data": {
                "meta": all_permissions['meta'],
                "items": all_permissions['data'],
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return handle_rest_exception_helper(e)


@swagger_auto_schema(
    method="get",
    operation_description="Get permission list by Group ID",
    manual_parameters=[
        page_openapi,
        page_size_openapi,
    ],
    responses={
        200: openapi.Response("OK", PermissionListQueryDocWrapperSerializer),
        401: openapi.Response("Unauthorized", openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "status": openapi.Schema(type=openapi.TYPE_INTEGER),
                "message": openapi.Schema(type=openapi.TYPE_STRING),
            },
        )),
    },
)
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])  # is_staff - not is_superuser
def get_permissions_group(request, pk):
    try:
        auth_service = container.auth_service()
        _, page_number, page_size = get_pagination_parameters_rest(
            request)

        permissions_list = auth_service.get_group_permissions(
            group_id=pk, page_number=page_number, page_size=page_size)
        return Response({
            "status": status.HTTP_200_OK,
            "message": "Permisos obtenidos exitosamente",
            "data": {
                "meta": permissions_list['meta'],
                "items": permissions_list['data'],
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return handle_rest_exception_helper(e)
