from rest_framework import status
from rest_framework.response import Response
from config.shared.helpers.handle_rest_exception_helper import handle_rest_exception_helper
from config.shared.helpers.pagination_helper import get_pagination_parameters_rest

from config.shared.services.base_mixins_service import (
    FindServiceMixin, PaginationServiceMixin
)
from rest_framework.views import APIView

from config.shared.views.base_mixins_view import (
    AuthenticationViewMixin, PermissionRequiredViewMixin, ListViewMixin, CreateViewMixin, UpdateViewMixin, RetrieveViewMixin, DestroyViewMixin,
    RetrievePkViewMixin,
    ListViewSalesMixin, RetrieveViewSalesMixin, CreateViewSalesMixin, UpdateViewSalesMixin,
    ListViewSalesMixinNoCache, RetrieveViewSalesMixinNoCache, CreateViewSalesMixinNoCache, UpdateViewSalesMixinNoCache,
    ListViewUserMixin, RetrieveViewUserMixin, CreateViewUserMixin, UpdateViewUserMixin, ListViewUserMixinNoCache, RetrieveViewUserMixinNoCache, CreateViewUserMixinNoCache, UpdateViewUserMixinNoCache,

    ListViewGenericNoPagingNoStructureMixin,

    BaseGenericPOSTView,

    BaseGenericGETALLNoCacheViewMixin,

    ListViewNoCacheMixin, CreateViewNoCacheMixin, UpdateViewNoCacheMixin, RetrieveViewMixinNoCache,

    get_schema_name,
    CacheViewMixin,

)

from config.shared.constants.constants import (
    PAGINATION_DEFAULT_PAGE_NUMBER,
    PAGINATION_DEFAULT_PAGE_SIZE,
)
from config.shared.utils.cache_static_helper import CacheStaticHelper

from config.shared.views.audit_log_mixin import AuditLogMixin


class GenericAPIViewService(AuthenticationViewMixin, PermissionRequiredViewMixin, ListViewMixin, CreateViewMixin):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


class GenericAPIViewServiceNoCache(AuthenticationViewMixin, PermissionRequiredViewMixin, ListViewNoCacheMixin, CreateViewNoCacheMixin):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


class GenericAPIDetailViewService(AuthenticationViewMixin, PermissionRequiredViewMixin, RetrieveViewMixin, UpdateViewMixin):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


class GenericAPIDetailAllViewService(AuthenticationViewMixin, PermissionRequiredViewMixin, CreateViewMixin, RetrieveViewMixin, UpdateViewMixin, DestroyViewMixin):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


class GenericApiUpdDelentViewService(AuthenticationViewMixin, PermissionRequiredViewMixin, UpdateViewMixin, DestroyViewMixin):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


# one method -----------------
class BaseGetAllView(AuthenticationViewMixin, PermissionRequiredViewMixin, ListViewMixin):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


# UUID
class BaseRetrieveUuidView(AuthenticationViewMixin, PermissionRequiredViewMixin, RetrieveViewMixin):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


class BaseRetrieveUuidViewNoCache(AuthenticationViewMixin, PermissionRequiredViewMixin, RetrieveViewMixinNoCache):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


class BaseRetrievePkView(AuthenticationViewMixin, PermissionRequiredViewMixin, RetrievePkViewMixin):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


class BaseUpdateView(AuthenticationViewMixin, PermissionRequiredViewMixin, UpdateViewMixin):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


class BaseUpdateViewNoCache(AuthenticationViewMixin, PermissionRequiredViewMixin, UpdateViewNoCacheMixin):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


# ### Sales views ------------------------------
class GenericSalesAPIViewService(AuthenticationViewMixin, PermissionRequiredViewMixin, ListViewSalesMixin, CreateViewSalesMixin):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


class BaseGetAllSalesView(AuthenticationViewMixin, PermissionRequiredViewMixin, ListViewSalesMixin):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


# UUID
class BaseRetrieveUuidSalesView(AuthenticationViewMixin, PermissionRequiredViewMixin, RetrieveViewSalesMixin):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


class BaseUpdateSalesView(AuthenticationViewMixin, PermissionRequiredViewMixin, UpdateViewSalesMixin):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


# sales views withouth cache -----------------
class BaseGetAllSalesNoCacheView(AuthenticationViewMixin, PermissionRequiredViewMixin, ListViewSalesMixinNoCache):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


class BaseRetrieveUuidSalesNoCacheView(AuthenticationViewMixin, PermissionRequiredViewMixin, RetrieveViewSalesMixinNoCache):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


class BaseCreateSalesNoCacheView(AuthenticationViewMixin, PermissionRequiredViewMixin, CreateViewSalesMixinNoCache):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


class BaseUpdateSalesNoCacheView(AuthenticationViewMixin, PermissionRequiredViewMixin, UpdateViewSalesMixinNoCache):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


# ### Free views ===========================================
class BaseGetAllFreeView(APIView, ListViewMixin):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


class BaseCreateFreeView(APIView, CreateViewMixin):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


class BaseCreateFreeCustomMethodView(APIView, BaseGenericPOSTView):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


class BaseRetrieveUuidFreeView(APIView, RetrieveViewMixin):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()

    def get(self, request, uuid):
        return super().get(request, uuid)


class BaseUpdateFreeView(APIView, UpdateViewMixin):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


# ### Generic User views ===========================================
class GenericUserAPIViewService(AuthenticationViewMixin, PermissionRequiredViewMixin, ListViewUserMixin, CreateViewUserMixin):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


class BaseGetAllUserView(AuthenticationViewMixin, PermissionRequiredViewMixin, ListViewUserMixin):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


# UUID
class BaseRetrieveUuidUserView(AuthenticationViewMixin, PermissionRequiredViewMixin, RetrieveViewUserMixin):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


class BaseCreateUserView(AuthenticationViewMixin, PermissionRequiredViewMixin, CreateViewUserMixin):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


class BaseUpdateUserView(AuthenticationViewMixin, PermissionRequiredViewMixin, UpdateViewUserMixin):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()


# ### Generic General Views NO repos,services, no normal structure ===========================================
class BaseGetAllGenericNoPagingNoStructureView(AuthenticationViewMixin, ListViewGenericNoPagingNoStructureMixin):
    # DI: service
    def __init__(self):
        super().__init__()


# ##### ================================
class GenericFindAuthPermNoCacheView(AuthenticationViewMixin, PermissionRequiredViewMixin, BaseGenericGETALLNoCacheViewMixin, FindServiceMixin, PaginationServiceMixin):
    # DI: service
    def __init__(self, service):
        self.service = service
        super().__init__()

    # aux methods ---------------
    def find_all_extended_qs(self, queryset, filter_params=None):
        """
        This method is used to extend the queryset with additional filters. You must return the queryset, even if you don't modify it.
        """
        return queryset

    def find_all_post_serializer(self, serialized_data, filter_params=None):
        """
        This method is used to extend the serialized data after the serialization process. You must return the serialized data, even if you don't modify it. Data is already paginated.
        """
        return serialized_data

    def find_all(self, filter_params=None, page_number=PAGINATION_DEFAULT_PAGE_NUMBER, page_size=PAGINATION_DEFAULT_PAGE_SIZE):
        queryset = self.find_all_mx(self.filter, filter_params)
        new_qs = self.find_all_extended_qs(queryset, filter_params)

        paginated_data = self.paginate_queryset(
            new_qs, page_number, page_size)
        serialized_data = self.serialize(paginated_data["page_obj"], many=True)
        serialized_data_x = self.find_all_post_serializer(
            serialized_data, filter_params)
        return {
            "meta": {
                "next": paginated_data["next_page"],
                "previous": paginated_data["previous_page"],
                "count": paginated_data["count"],
                "total_pages": paginated_data["total_pages"],
            },
            "data": serialized_data_x,
        }


class BaseViewMixin(APIView):
    pass


# ##### CACHE ===============================
class BaseGenericFindOneByFieldView(AuthenticationViewMixin, PermissionRequiredViewMixin):
    def get_mxv(self, request, field, args={}):
        try:
            serialized_data = self.generic_get_method(request, field, args)

            return Response(
                {
                    'status': args.get('success_status', status.HTTP_200_OK),
                    'message': args.get('success_message', 'Elemento encontrado'),
                    'data': serialized_data
                },
                status=args.get('success_status', status.HTTP_200_OK)
            )
        except Exception as e:
            return handle_rest_exception_helper(e)

    def generic_get_method(self, request, field, args={}):
        """
        Must be implemented in the child class to handle the get request with custom service method
        """
        pass


class BaseGenericPATCHByFieldView(AuthenticationViewMixin, PermissionRequiredViewMixin, CacheViewMixin):
    def patch_mxv(self, request, field, args={}):
        try:
            serialized_data = self.generic_patch_method(request, field, args)
            self.clear_cache(schema_name=get_schema_name(request))
            return Response(
                {
                    'status': args.get('success_status', status.HTTP_200_OK),
                    'message': args.get('success_message', 'Elemento actualizado'),
                    'data': serialized_data
                },
                status=args.get('success_status', status.HTTP_200_OK)
            )
        except Exception as e:
            return handle_rest_exception_helper(e)

    def generic_patch_method(self, request, field, args={}):
        """
        Must be implemented in the child class to handle the patch request with custom service method
        """
        pass


# ##### NO CACHE ===============================
class BaseGenericFindOneByFieldNoCacheView(AuthenticationViewMixin, PermissionRequiredViewMixin):

    def get_mxv(self, request, field):
        try:
            serialized_data = self.generic_get_method(request, field)

            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elemento encontrado',
                    'data': serialized_data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return handle_rest_exception_helper(e)

    def generic_get_method(self, request, field):
        """
        Must be implemented in the child class to handle the get request with custom service method
        """
        pass


class BaseGenericFindAllNoCacheView(AuthenticationViewMixin, PermissionRequiredViewMixin):
    def get_mxv(self, request, no_serialize=False):
        try:
            filter_params, page_number, page_size = get_pagination_parameters_rest(
                request)

            serialized_data = self.generic_get_method(
                request, filter_params, page_number, page_size)
            if not no_serialize:
                return Response(
                    {
                        'status': status.HTTP_200_OK,
                        'message': 'Elementos encontrados',
                        'data': {
                            'meta': serialized_data.get('meta', None),
                            'items': serialized_data.get('data', None)
                        }
                    },
                    status=status.HTTP_200_OK
                )
            # total response override ----
            return serialized_data

        except Exception as e:
            return handle_rest_exception_helper(e)

    def generic_get_method(self, request, filter_params, page_number, page_size):
        """
        Must be implemented in the child class to handle the get request with custom service method
        """
        pass


class BaseGenericPATCHNoCacheView(AuditLogMixin, PermissionRequiredViewMixin):
    def patch_mxv(self, request, pk):
        try:
            serialized_data = self.generic_patch_method(request, pk)

            rid = self._extract_rid(serialized_data, fallback=pk)
            self._audit_safe(
                request, action="PATCH", description="Generic PATCH NoCache OK", resource_id=rid,
                extra={"payload_keys": list(
                    request.data.keys()), "nocache": True}
            )

            return Response(
                {'status': status.HTTP_200_OK,
                    'message': 'Elemento Actualizado', 'data': serialized_data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            self._audit_safe(
                request, action="PATCH FAILED", description=str(e), resource_id=pk,
                extra={"payload_keys": list(
                    request.data.keys()), "nocache": True, "error": str(e)},
                outcome="FAILED"
            )
            return handle_rest_exception_helper(e)


class BaseGenericPATCHByFieldNoCacheView(AuditLogMixin, PermissionRequiredViewMixin):
    def patch_mxv(self, request, field):
        try:
            serialized_data = self.generic_patch_method(request, field)

            rid = self._extract_rid(serialized_data)
            self._audit_safe(
                request, action="PATCH", description="Generic PATCH Field NoCache OK", resource_id=rid,
                extra={"payload_keys": list(
                    request.data.keys()), "field": field, "nocache": True}
            )

            return Response(
                {'status': status.HTTP_200_OK,
                    'message': 'Elemento Actualizado', 'data': serialized_data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            self._audit_safe(
                request, action="PATCH FAILED", description=str(e),
                extra={"payload_keys": list(
                    request.data.keys()), "field": field, "nocache": True, "error": str(e)},
                outcome="FAILED"
            )
            return handle_rest_exception_helper(e)

class BaseGenericPOSTNoCacheAuthOnlyView(AuditLogMixin, AuthenticationViewMixin):
    def post_mxv(self, request, args={'success_message': 'Elemento creado', 'success_status': status.HTTP_200_OK, 'total_response_override': False}):
        try:
            serialized_data = self.generic_post_method(request, args)
            if args.get('total_response_override', False):
                return serialized_data

            rid = self._extract_rid(serialized_data)
            self._audit_safe(
                request, action="CREATE", description="POST AuthOnly OK", resource_id=rid,
                extra={"payload_keys": list(
                    request.data.keys()), "auth_only": True}
            )

            return Response(
                {'status': args.get('success_status', status.HTTP_200_OK), 'message': args.get(
                    'success_message', 'Elemento creado'), 'data': serialized_data},
                status=args.get('success_status', status.HTTP_200_OK)
            )
        except Exception as e:
            self._audit_safe(
                request, action="CREATE FAILED", description=str(e),
                extra={"payload_keys": list(
                    request.data.keys()), "auth_only": True, "error": str(e)},
                outcome="FAILED"
            )
            return handle_rest_exception_helper(e)

# #### FREE VIEWS ===================================
class BaseGenericPOSTNoCacheFreeView(AuditLogMixin, APIView):
    def post_mxv(self, request, args={}):
        try:
            serialized_data = self.generic_post_method(request, args)

            rid = self._extract_rid(serialized_data)
            self._audit_safe(
                request, action="CREATE", description="POST Free NoCache OK", resource_id=rid,
                extra={"payload_keys": list(request.data.keys()), "free": True}
            )

            return Response(
                {'status': args.get('success_status', status.HTTP_201_CREATED), 'message': args.get(
                    'success_message', 'Elemento creado'), 'data': serialized_data},
                status=args.get('success_status', status.HTTP_201_CREATED)
            )
        except Exception as e:
            self._audit_safe(
                request, action="CREATE FAILED", description=str(e),
                extra={"payload_keys": list(
                    request.data.keys()), "free": True, "error": str(e)},
                outcome="FAILED"
            )
            return handle_rest_exception_helper(e)

class BaseGenericGetAllNoCacheFreeView(APIView):
    # total_response_override: send acutal Response
    def get_mxv(self, request, total_response_override=False):
        try:
            filter_params, page_number, page_size = get_pagination_parameters_rest(
                request)

            res = self.generic_get_method(
                request, filter_params, page_number, page_size)
            if total_response_override:
                return res

            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elementos encontrados',
                    'data': {
                        'meta': res.get('meta', None),
                        'items': res.get('data', None)
                    }
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return handle_rest_exception_helper(e)

    def generic_get_method(self, request, filter_params, page_number, page_size):
        """
        Must be implemented in the child class to handle the get request with custom service method
        """
        pass


class BaseGenericGetAllNoCacheAuthPermView(AuthenticationViewMixin, PermissionRequiredViewMixin, BaseGenericGetAllNoCacheFreeView):
    def get_mxv(self, request, total_response_override=False):
        try:
            filter_params, page_number, page_size = get_pagination_parameters_rest(
                request)

            res = self.generic_get_method(
                request, filter_params, page_number, page_size)
            if total_response_override:
                return res

            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elementos encontrados',
                    'data': {
                        'meta': res.get('meta', None),
                        'items': res.get('data', None)
                    }
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return handle_rest_exception_helper(e)


class BaseGenericFindOneByFieldNoCacheFreeView(APIView):
    def get_mxv(self, request, args={}):
        try:
            serialized_data = self.generic_get_method(request, args)

            if args.get('total_response_override', False):
                return serialized_data

            return Response(
                {
                    'status': args.get('success_status', status.HTTP_200_OK),
                    'message': args.get('success_message', 'Elemento encontrado'),
                    'data': serialized_data
                },
                status=args.get('success_status', status.HTTP_200_OK)
            )
        except Exception as e:
            return handle_rest_exception_helper(e)

    def generic_get_method(self, request, args={}):
        """
        Must be implemented in the child class to handle the get request with custom service method
        """
        pass


# ----------------
class BaseGenericFindOneByFieldNoCacheAuthPermView(AuthenticationViewMixin, PermissionRequiredViewMixin):
    def get_mxv(self, request,  args={}):
        try:
            serialized_data = self.generic_get_method(request, args)

            return Response(
                {
                    'status': args.get('success_status', status.HTTP_200_OK),
                    'message': args.get('success_message', 'Elemento encontrado'),
                    'data': serialized_data
                },
                status=args.get('success_status', status.HTTP_200_OK)
            )
        except Exception as e:
            return handle_rest_exception_helper(e)

    def generic_get_method(self, request, args={}):
        """
        Must be implemented in the child class to handle the get request with custom service method
        """
        pass


class BaseGenericFindOneByFieldNoCacheAuthOnlyView(AuthenticationViewMixin):
    def get_mxv(self, request, args={}):
        try:
            serialized_data = self.generic_get_method(request, args)

            return Response(
                {
                    'status': args.get('success_status', status.HTTP_200_OK),
                    'message': args.get('success_message', 'Elemento encontrado'),
                    'data': serialized_data
                },
                status=args.get('success_status', status.HTTP_200_OK)
            )
        except Exception as e:
            return handle_rest_exception_helper(e)

    def generic_get_method(self, request, args={}):
        """
        Must be implemented in the child class to handle the get request with custom service method
        """
        pass


class BaseGenericPATCHByFieldNoCacheAuthOnlyView(AuditLogMixin, AuthenticationViewMixin):
    def patch_mxv(self, request, args={}):
        try:
            serialized_data = self.generic_patch_method(request, args)

            rid = self._extract_rid(serialized_data)
            self._audit_safe(
                request, action="PATCH", description="PATCH Field AuthOnly OK", resource_id=rid,
                extra={"payload_keys": list(
                    request.data.keys()), "auth_only": True}
            )

            return Response(
                {'status': args.get('success_status', status.HTTP_200_OK), 'message': args.get(
                    'success_message', 'Elemento actualizado'), 'data': serialized_data},
                status=args.get('success_status', status.HTTP_200_OK)
            )
        except Exception as e:
            self._audit_safe(
                request, action="PATCH FAILED", description=str(e),
                extra={"payload_keys": list(
                    request.data.keys()), "auth_only": True, "error": str(e)},
                outcome="FAILED"
            )
            return handle_rest_exception_helper(e)

# -----------------
class BaseGenericPATCHByFieldNoCacheAuthPermView(AuditLogMixin, AuthenticationViewMixin, PermissionRequiredViewMixin):
    def patch_mxv(self, request, field, args={}):
        try:
            serialized_data = self.generic_patch_method(request, field, args)

            rid = self._extract_rid(serialized_data)
            self._audit_safe(
                request, action="PATCH", description="PATCH Field AuthPerm OK", resource_id=rid,
                extra={"payload_keys": list(
                    request.data.keys()), "field": field, "auth_perm": True}
            )

            return Response(
                {'status': args.get('success_status', status.HTTP_200_OK), 'message': args.get(
                    'success_message', 'Elemento actualizado'), 'data': serialized_data},
                status=args.get('success_status', status.HTTP_200_OK)
            )
        except Exception as e:
            self._audit_safe(
                request, action="PATCH FAILED", description=str(e),
                extra={"payload_keys": list(
                    request.data.keys()), "field": field, "auth_perm": True, "error": str(e)},
                outcome="FAILED"
            )
            return handle_rest_exception_helper(e)

    def generic_patch_method(self, request, field, args={}):
        """
        Must be implemented in the child class to handle the patch request with custom service method
        """
        pass

class BaseGenericPOSTNoCacheAuthPermView(AuditLogMixin, AuthenticationViewMixin, PermissionRequiredViewMixin):
    def post_mxv(self, request, args={'total_response_override': False}):
        try:
            serialized_data = self.generic_post_method(request, args)
            if args.get('total_response_override', False):
                return serialized_data

            rid = self._extract_rid(serialized_data)
            self._audit_safe(
                request, action="CREATE", description="POST NoCache AuthPerm OK", resource_id=rid,
                extra={"payload_keys": list(
                    request.data.keys()), "auth_perm": True}
            )

            try:
                cache_key = args.get(
                    'cache_key', None) or self.service.repository.model.__name__
                CacheStaticHelper.clear_all_model_cache(cache_key)
            except Exception:
                pass

            return Response(
                {'status': args.get('success_status', status.HTTP_201_CREATED), 'message': args.get(
                    'success_message', 'Elemento creado'), 'data': serialized_data},
                status=args.get('success_status', status.HTTP_201_CREATED)
            )
        except Exception as e:
            self._audit_safe(
                request, action="CREATE FAILED", description=str(e),
                extra={"payload_keys": list(
                    request.data.keys()), "auth_perm": True, "error": str(e)},
                outcome="FAILED"
            )
            return handle_rest_exception_helper(e)

    def generic_post_method(self, request, args={}):
        """
        Must be implemented in the child class to handle the post request with custom service method
        """
        pass

class BaseGenericPOSTAuthPermView(AuditLogMixin, AuthenticationViewMixin, PermissionRequiredViewMixin):
    def post_mxv(self, request, args={}):
        try:
            serialized_data = self.generic_post_method(request, args)

            rid = self._extract_rid(serialized_data)
            self._audit_safe(
                request, action="CREATE", description="POST AuthPerm OK", resource_id=rid,
                extra={"payload_keys": list(
                    request.data.keys()), "auth_perm": True}
            )

            try:
                cache_key = args.get(
                    'cache_key', None) or self.service.repository.model.__name__
                CacheStaticHelper.clear_all_model_cache(cache_key)
            except Exception:
                pass

            return Response(
                {'status': args.get('success_status', status.HTTP_201_CREATED), 'message': args.get(
                    'success_message', 'Elemento creado'), 'data': serialized_data},
                status=args.get('success_status', status.HTTP_201_CREATED)
            )
        except Exception as e:
            self._audit_safe(
                request, action="CREATE FAILED", description=str(e),
                extra={"payload_keys": list(
                    request.data.keys()), "auth_perm": True, "error": str(e)},
                outcome="FAILED"
            )
            return handle_rest_exception_helper(e)

class BaseGenericPOSTFreeView(AuditLogMixin, APIView):
    def post_mxv(self, request, args={}):
        try:
            serialized_data = self.generic_post_method(request, args)

            rid = self._extract_rid(serialized_data)
            self._audit_safe(
                request, action="CREATE", description="POST Free OK", resource_id=rid,
                extra={"payload_keys": list(request.data.keys()), "free": True}
            )

            try:
                cache_key = args.get(
                    'cache_key', None) or self.service.repository.model.__name__
                CacheStaticHelper.clear_all_model_cache(cache_key)
            except Exception:
                pass

            return Response(
                {'status': args.get('success_status', status.HTTP_201_CREATED), 'message': args.get(
                    'success_message', 'Elemento creado'), 'data': serialized_data},
                status=args.get('success_status', status.HTTP_201_CREATED)
            )
        except Exception as e:
            self._audit_safe(
                request, action="CREATE FAILED", description=str(e),
                extra={"payload_keys": list(
                    request.data.keys()), "free": True, "error": str(e)},
                outcome="FAILED"
            )
            return handle_rest_exception_helper(e)
