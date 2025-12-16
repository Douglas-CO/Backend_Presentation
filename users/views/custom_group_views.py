from rest_framework import status
from rest_framework.response import Response

# ## docs openapi
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from config.shared.di.di import container
from config.shared.views.general_view import (
    GenericAPIViewService,
    GenericAPIDetailAllViewService,
    BaseRetrieveUuidView,
)
from config.shared.serializers.serializers import (
    BadRequestSerializer,
    NotFoundSerializer,
)

from config.shared.constants.constants import page_size_openapi, page_openapi
from users.serializers.custom_group_serializers import (
    CustomGroupSerializer,
    CustomGroupQueryDocWrapperSerializer,
    CustomGroupOptDocWrapperSerializer,
    CustomGroupFilterSerializer,
)


class CustomGroupView(GenericAPIViewService):

    # constructor: DI
    def __init__(self):
        custom_group_service = container.custom_group_service()
        super().__init__(custom_group_service)

    @swagger_auto_schema(
        operation_description="Get All CustomGroups",
        responses={
            200: openapi.Response("OK", CustomGroupQueryDocWrapperSerializer),
        },
        query_serializer=CustomGroupFilterSerializer,
        manual_parameters=[page_size_openapi, page_openapi],
    )
    def get(self, request):
        return super().get(request)

    @swagger_auto_schema(
        operation_description="Create CustomGroup",
        request_body=CustomGroupSerializer,
        responses={
            201: openapi.Response("OK", CustomGroupOptDocWrapperSerializer),
            400: openapi.Response("Bad Request", BadRequestSerializer),
        },
    )
    def post(self, request):
        return super().post(request)


class CustomGroupDetailView(GenericAPIDetailAllViewService):

    # constructor: DI
    def __init__(self):
        custom_group_service = container.custom_group_service()
        super().__init__(custom_group_service)

    @swagger_auto_schema(
        auto_schema=None,
        operation_description="Get CustomGroup by ID",
        responses={
            200: openapi.Response("OK", CustomGroupOptDocWrapperSerializer),
            404: openapi.Response("Not Found", NotFoundSerializer),
        },
    )
    def get(self, request, pk):
        return Response({"status": status.HTTP_404_NOT_FOUND, "message": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Update CustomGroup",
        request_body=CustomGroupSerializer,
        responses={
            200: openapi.Response("OK", CustomGroupOptDocWrapperSerializer),
            404: openapi.Response("Not Found", NotFoundSerializer),
            400: openapi.Response("Bad Request", BadRequestSerializer),
        },
    )
    def patch(self, request, pk):
        return super().patch(request, pk)

    @swagger_auto_schema(
        operation_description="Delete CustomGroup",
        responses={
            204: openapi.Response("Ok - No Content"),
            404: openapi.Response("Not Found", NotFoundSerializer),
            401: openapi.Response('Unauthorized'),
        },
    )
    def delete(self, request, pk):
        return super().delete(request, pk)


class CustomGroupDetailViewByUuid(BaseRetrieveUuidView):
    # constructor: DI
    def __init__(self):
        custom_group_service = container.custom_group_service()
        super().__init__(custom_group_service)

    @swagger_auto_schema(
        operation_description="Get CustomGroup by UUID",
        responses={
            200: openapi.Response("OK", CustomGroupOptDocWrapperSerializer),
            404: openapi.Response("Not Found", NotFoundSerializer),
        },
    )
    def get(self, request, uuid):
        return super().get(request, uuid)
