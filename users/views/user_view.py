# ## docs openapi
from config.shared.views.base_mixins_view import AuthenticationViewMixin, PermissionRequiredViewMixin, BaseGenericPATCHView
from users.services.user_service import UserService
from config.shared.serializers.serializers import NotFoundSerializer
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework import status
from rest_framework.response import Response

from config.shared.helpers.pagination_helper import get_pagination_parameters_rest
from config.shared.di.di import container
from config.shared.serializers.serializers import (
    BadRequestSerializer
)
from config.shared.views.general_view import GenericApiUpdDelentViewService
from config.shared.helpers.handle_rest_exception_helper import (
    handle_rest_exception_helper,
)
from config.shared.constants.constants import page_size_openapi, page_openapi

from users.serializers.user_serializers import (
    UserCreateSerializer,
    UserOptDocWrapperSerializer,
    UserQueryDocWrapperSerializer,
    UserFilterSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
)
from config.shared.views.general_view import (
    BaseGenericPATCHNoCacheView,
)

# from users.services.user_service import UserService
from rest_framework.decorators import api_view


# auth and permissions
from rest_framework.authentication import TokenAuthentication  # permissions
from rest_framework.permissions import IsAuthenticated  # authentication
from rest_framework.decorators import authentication_classes, permission_classes


@swagger_auto_schema(
    method="POST",
    operation_description="Create User",
    request_body=UserCreateSerializer,
    responses={
        201: openapi.Response("OK", UserOptDocWrapperSerializer),
        400: openapi.Response("Bad Request", BadRequestSerializer),
    },
)
@api_view(['POST'])
@authentication_classes(
    [TokenAuthentication]
)  # Requiere Header Authorization con 'Token <token>' - method to authenticate
@permission_classes([IsAuthenticated])  # Authent
def user_create_view(request):
    try:
        service = container.user_service()
        serialized_instance = service.create_user(data=request.data)
        return Response({
            "status": status.HTTP_201_CREATED,
            "message": "Usuario creado exitosamente",
            "data": serialized_instance,
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return handle_rest_exception_helper(e)


@swagger_auto_schema(
    method="GET",
    operation_description="Get All Candys",
    responses={
        200: openapi.Response("OK", UserQueryDocWrapperSerializer),
        401: openapi.Response("Unauthorized"),
        403: openapi.Response("Forbidden"),
    },
    query_serializer=UserFilterSerializer,
    manual_parameters=[page_size_openapi, page_openapi],
)
@api_view(['GET'])
@authentication_classes(
    [TokenAuthentication]
)  # Requiere Header Authorization con 'Token <token>' - method to authenticate
@permission_classes([IsAuthenticated])  # Authent
def get_all(request):
    try:
        filter_params, page_number, page_size = get_pagination_parameters_rest(
            request)

        service = container.user_service()
        serialized_instances = service.find_all(
            filter_params, page_number, page_size
        )

        return Response({
            "status": status.HTTP_200_OK,
            "message": "Usuarios encontrados",
            "data": {
                "meta": serialized_instances["meta"],
                "items": serialized_instances["data"],
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return handle_rest_exception_helper(e)


class UserDetailUUIDView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    service = UserService

    def __init__(self):
        self.service = container.user_service()

    @swagger_auto_schema(
        operation_description="Detalle de Usuario",
        responses={
            200: openapi.Response("OK", UserOptDocWrapperSerializer),
            404: openapi.Response("Not Found", NotFoundSerializer),
            401: openapi.Response("Unauthorized"),
            403: openapi.Response("Forbidden"),
        },
    )
    def get(self, request, uuid):
        try:
            serialized_instance = self.service.find_one_by_uuid(uuid)
            return Response({
                "status": status.HTTP_200_OK,
                "message": "Usuario encontrado",
                "data": serialized_instance,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return self.handle_exception(e)

    def handle_exception(self, exc):
        return handle_rest_exception_helper(exc)


class UserDetailView(GenericApiUpdDelentViewService):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    service = UserService

    # constructor: DI
    def __init__(self):
        user_service = container.user_service()
        super().__init__(user_service)

    @swagger_auto_schema(
        operation_description="Get User",
        responses={
            200: openapi.Response("OK", UserOptDocWrapperSerializer),
            404: openapi.Response("Not Found", NotFoundSerializer),
            401: openapi.Response("Unauthorized"),
            403: openapi.Response("Forbidden"),
        },
    )
    def get(self, request, pk):
        try:
            serialized_instance = self.service.find_one(pk)
            return Response({
                "status": status.HTTP_200_OK,
                "message": "Usuario encontrado",
                "data": serialized_instance,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return self.handle_exception(e)

    @swagger_auto_schema(
        operation_description="Update Candy",
        request_body=UserUpdateSerializer,
        responses={
            200: openapi.Response("OK", UserOptDocWrapperSerializer),
            404: openapi.Response("Not Found", NotFoundSerializer),
            400: openapi.Response("Bad Request", BadRequestSerializer),
            401: openapi.Response("Unauthorized"),
            403: openapi.Response("Forbidden"),
        },
    )
    def patch(self, request, pk):
        return super().patch(request, pk)

    @swagger_auto_schema(
        operation_description="Eliminar Usuario",
        responses={
            204: openapi.Response("OK"),
            404: openapi.Response("Not Found", NotFoundSerializer),
            401: openapi.Response("Unauthorized"),
            403: openapi.Response("Forbidden"),
        },
    )
    def delete(self, request, pk):
        is_admin = request.user.is_staff and request.user.is_superuser
        if not is_admin:
            return Response({
                "status": status.HTTP_403_FORBIDDEN,
                "message": "No tienes permisos para realizar esta acción",
            }, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, pk)

    def handle_exception(self, exc):
        return handle_rest_exception_helper(exc)


class UnblockUserView(AuthenticationViewMixin, PermissionRequiredViewMixin, BaseGenericPATCHView):

    # constructor: DI
    def __init__(self):
        self.service = container.user_service()

    @swagger_auto_schema(
        operation_description="Desbloquear Usuario",
        responses={
            200: openapi.Response("OK", UserOptDocWrapperSerializer),
            404: openapi.Response("Not Found", NotFoundSerializer),
            400: openapi.Response("Bad Request", BadRequestSerializer),
            401: openapi.Response("Unauthorized"),
            403: openapi.Response("Forbidden"),
        },
    )
    def patch(self, request, pk):
        return super().patch_mxv(request, pk)

    def generic_patch_method(self, request, pk):
        return self.service.unblock_user(pk)


# ### CUSTOM VIEWS ========================
class ChangePasswordView(BaseGenericPATCHNoCacheView):

    def __init__(self):
        self.service = container.user_service()

    @swagger_auto_schema(
        operation_description="Change User Password",
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response("OK", UserOptDocWrapperSerializer),
            404: openapi.Response("Not Found", NotFoundSerializer),
            400: openapi.Response("Bad Request", BadRequestSerializer),
        },
    )
    def patch(self, request, id):
        return super().patch_mxv(request, id)

    def generic_patch_method(self, request, field):
        return self.service.change_password(
            data=request.data,
            pk=field,
            user_i=request.user
        )


class DeactivateUserView(BaseGenericPATCHNoCacheView):

    def __init__(self):
        self.service = container.user_service()

    @swagger_auto_schema(
        operation_description="Deactivate User",
        responses={
            200: openapi.Response("OK", UserOptDocWrapperSerializer),
            404: openapi.Response("Not Found", NotFoundSerializer),
            400: openapi.Response("Bad Request", BadRequestSerializer),
        },
    )
    def patch(self, request, id):
        return super().patch_mxv(request, id)

    def generic_patch_method(self, request, px):
        return self.service.desactivate_user(
            pk=px,
            user_i=request.user
        )
