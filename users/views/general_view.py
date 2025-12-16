from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response

from users.shared.constants.system_modules import system_modules_sidenav


@swagger_auto_schema(
    method="get",
    operation_description="Generate a temporary link to upload a file to MinIO",
    manual_parameters=[
        openapi.Parameter(
            'file_name', openapi.IN_QUERY, type=openapi.TYPE_STRING,
            description="The name of the file in MinIO", required=True
        ),
        openapi.Parameter(
            'expiration', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
            description="Expiration time of the link in seconds (default 1 hour)"
        ),
    ],
    responses={
        200: openapi.Response("OK", openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'message': openapi.Schema(type=openapi.TYPE_STRING),
                'code': openapi.Schema(type=openapi.TYPE_INTEGER),
                'data': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )),
        401: "Unauthorized",
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def generate_temporary_upload_link(request):
    file_name = request.GET.get('file_name', None)
    expiration = request.GET.get('expiration', 3600)

    if not file_name:
        return Response({
            'status': 'error',
            'message': 'The file_name parameter is required',
            'code': 400,
        })

    try:
        expiration = int(expiration)
    except ValueError:
        return Response({
            'status': 'error',
            'message': 'The expiration parameter must be an integer',
            'code': 400,
        })


@swagger_auto_schema(
    method="get",
    operation_description="Get all system modules (Sidenav)",
    responses={
        200: openapi.Response("OK", openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'message': openapi.Schema(type=openapi.TYPE_STRING),
                'code': openapi.Schema(type=openapi.TYPE_INTEGER),
                'data': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING)
                ),
            }
        )),
        401: "Unauthorized",
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_system_modules(request):
    all_modules = system_modules_sidenav

    return Response({
        'status': 'success',
        'message': 'Módulos del sistema obtenidos correctamente',
        'code': 200,
        'data': all_modules
    })
