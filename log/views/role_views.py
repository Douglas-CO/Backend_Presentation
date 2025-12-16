# ## docs openapi
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from config.shared.di.di import container
from config.shared.views.general_view import (
    GenericAPIViewService,
    BaseUpdateView,
    BaseRetrieveUuidView,
)
from config.shared.serializers.serializers import (
    BadRequestSerializer,
    NotFoundSerializer,
)

from config.shared.constants.constants import page_size_openapi, page_openapi
from log.serializers.role_serializers import (
    RoleSerializer,
    RoleQueryDocWrapperSerializer,
    RoleOptDocWrapperSerializer,
    RoleFilterSerializer,
)


class RoleView(GenericAPIViewService):

    # constructor: DI
    def __init__(self):
        role_service = container.role_service()
        super().__init__(role_service)

    @swagger_auto_schema(
        operation_description="Get All Roles",
        responses={
            200: openapi.Response("OK", RoleQueryDocWrapperSerializer),
        },
        query_serializer=RoleFilterSerializer,
        manual_parameters=[page_size_openapi, page_openapi],
    )
    def get(self, request):
        return super().get(request)

    @swagger_auto_schema(
        operation_description="Create Role",
        request_body=RoleSerializer,
        responses={
            201: openapi.Response("OK", RoleOptDocWrapperSerializer),
            400: openapi.Response("Bad Request", BadRequestSerializer),
        },
    )
    def post(self, request):
        return super().post(request)


class RoleDetailView(BaseUpdateView):

    # constructor: DI
    def __init__(self):
        role_service = container.role_service()
        super().__init__(role_service)

    @swagger_auto_schema(
        operation_description="Update Role",
        request_body=RoleSerializer,
        responses={
            200: openapi.Response("OK", RoleOptDocWrapperSerializer),
            404: openapi.Response("Not Found", NotFoundSerializer),
            400: openapi.Response("Bad Request", BadRequestSerializer),
        },
    )
    def patch(self, request, pk):
        return super().patch(request, pk)

class RoleDetailViewByUuid(BaseRetrieveUuidView):
    # constructor: DI
    def __init__(self):
        role_service = container.role_service()
        super().__init__(role_service)

    @swagger_auto_schema(
        operation_description="Get Role by UUID",
        responses={
            200: openapi.Response("OK", RoleOptDocWrapperSerializer),
            404: openapi.Response("Not Found", NotFoundSerializer),
        },
    )
    def get(self, request, uuid):
        return super().get(request, uuid)
