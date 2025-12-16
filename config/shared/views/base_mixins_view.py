import inspect
from abc import ABC, abstractmethod
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# authentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission
from rest_framework.authentication import TokenAuthentication

# custom user state validation
from django.utils.translation import gettext_lazy as _

# authorization
from django.core.exceptions import PermissionDenied

# cache
from django.core.cache import cache
from config.shared.utils.redis_utils import (
    generate_cache_key, clear_cache_key_get_all, generate_cache_key_generic_one_field, get_filter_string
)

#
from config.shared.utils.common_utils import (
    generate_cache_key, clear_cache_key_get_all
)
from config.shared.helpers.pagination_helper import get_pagination_parameters_rest
from config.shared.helpers.handle_rest_exception_helper import handle_rest_exception_helper

from config.shared.constants.envs_constants import env

from config.shared.views.audit_log_mixin import AuditLogMixin


class IsActiveUser(BasePermission):
    message = _('Tu cuenta está inactiva.')

    def has_permission(self, request, view):
        user = request.user

        if user and user.is_authenticated:
            return getattr(user, 'state', False)
        return True


class AuthenticationViewMixin(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsActiveUser]


class AuthAdminViewMixin(APIView):
    authentication_classes = [TokenAuthentication]
    # is_staff - not is_superuser
    permission_classes = [IsAuthenticated, IsAdminUser, IsActiveUser]


class PermissionRequiredViewMixin(APIView):
    def check_permissions(self, request):
        app_table_name = self.service.repository.model._meta.db_table
        table_name = app_table_name.split('_')[1]
        app_name = app_table_name.split('_')[0]
        if request.method == 'GET':
            if not request.user.has_perm(f'{app_name}.view_{table_name}'):
                raise PermissionDenied()
        elif request.method == 'POST':
            if not request.user.has_perm(f'{app_name}.add_{table_name}'):
                # permitir lectura con post en ciertos casos -----
                allowed_permissions_view = [
                    'clientes.view_cliente'
                ]
                allowed_endpoint_view = [
                    '/api/v1/cliente/find-by-identification/'
                ]
                if not any([request.user.has_perm(perm) for perm in allowed_permissions_view]) or request.path not in allowed_endpoint_view:
                    raise PermissionDenied()

        elif request.method in ['PUT', 'PATCH']:
            if not request.user.has_perm(f'{app_name}.change_{table_name}'):
                raise PermissionDenied()
        elif request.method == 'DELETE':
            if not request.user.has_perm(f'{app_name}.delete_{table_name}'):
                raise PermissionDenied()
        return super().check_permissions(request)


class CacheViewMixin:
    def get_cache_key(self, filter_params):
        return generate_cache_key(filter_params=filter_params, model_name=self.service.repository.model.__name__)

    def get_cached_data(self, cache_key):
        return cache.get(cache_key)

    def set_cached_data(self, cache_key, data):
        cache.set(cache_key, data, timeout=int(
            env.str('REDIS_TIMEOUT')))

    def clear_cache(self, schema_name=None, model_name=None):
        repo_model_name = None
        if hasattr(self.service, 'repository') and self.service.repository:
            repo_model_name = self.service.repository.model.__name__
        model_name = model_name if model_name else repo_model_name
        cache.delete(f"{model_name}_all")
        cache.delete(f"{model_name}_one")
        # cache.delete(f"{model_name}{schema_name}_one")
        clear_cache_key_get_all(model_name)
        self.clear_find_one_related_cache(schema_name)

    def clear_model_related_cache(self, model_name):
        cache.delete_pattern(f"{model_name}*")

    def clear_find_one_related_cache(self, schema_name):
        cache.delete_pattern(f"*{schema_name}*_one")
        cache.delete_pattern(f"*{schema_name}*__one")


class ListViewMixin(CacheViewMixin):
    def get(self, request, ignorar_user=False):
        try:
            filter_params, page_number, page_size = get_pagination_parameters_rest(
                request)
            # ## cache debe considerar tenant company
            schema_name = get_schema_name(request)
            cache_key = self.get_cache_key({
                **filter_params, **{'schema_name': schema_name}
            })
            cache_data = self.get_cached_data(cache_key)

            if cache_data:
                return Response(
                    {
                        'status': status.HTTP_200_OK,
                        'message': 'Elementos paginados correctamente',
                        'data': {
                            'meta': cache_data['meta'],
                            'items': cache_data['data'],
                        }
                    },
                    status=status.HTTP_200_OK
                )

            try:
                serialized_instances = self.service.find_all(
                    filter_params, page_number, page_size, ignorar_user=ignorar_user)
            except:
                serialized_instances = self.service.find_all(
                    filter_params, page_number, page_size)
            self.set_cached_data(
                cache_key, {
                    'meta': serialized_instances['meta'], 'data': serialized_instances['data']}
            )

            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elementos paginados correctamente',
                    'data': {
                        'meta': serialized_instances['meta'],
                        'items': serialized_instances['data'],
                    }
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return handle_rest_exception_helper(e)


class ListViewNoCacheMixin:
    def get(self, request, ignorar_user=False):
        try:
            filter_params, page_number, page_size = get_pagination_parameters_rest(
                request)
            try:
                serialized_instances = self.service.find_all(
                    filter_params, page_number, page_size, ignorar_user=ignorar_user)
            except:
                serialized_instances = self.service.find_all(
                    filter_params, page_number, page_size)
            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elementos paginados correctamente',
                    'data': {
                        'meta': serialized_instances['meta'],
                        'items': serialized_instances['data'],
                    }
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return handle_rest_exception_helper(e)


class CreateViewMixin(AuditLogMixin, CacheViewMixin):
    def post(self, request):
        try:
            req_data_copy = request.data.copy()
            req_data_copy['custom_user_ixz'] = request.user
            serialized_instance = self.service.create(req_data_copy)

            self.audit_create_success(request, serialized_instance)

            self.clear_cache(schema_name=get_schema_name(request))
            return Response(
                {"status": status.HTTP_201_CREATED, "message": "Elemento creado correctamente", "data": serialized_instance},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            self.audit_create_failed(request, e)
            return handle_rest_exception_helper(e)

class CreateViewNoCacheMixin(AuditLogMixin):
    def post(self, request):
        try:
            serialized_instance = self.service.create(request.data)

            rid = self._extract_rid(serialized_instance)
            self._audit_safe(
                request,
                action="CREATE",
                description="Create OK",
                resource_id=rid,
                extra={"payload_keys": list(request.data.keys())},
            )

            return Response(
                {"status": status.HTTP_201_CREATED, "message": "Elemento creado correctamente", "data": serialized_instance},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            self._audit_safe(
                request,
                action="CREATE FAILED",
                description=str(e),
                extra={"payload_keys": list(request.data.keys()), "error": str(e)},
                outcome="FAILED",
            )
            return handle_rest_exception_helper(e)

# UUID
class RetrieveViewMixin(CacheViewMixin):
    def get(self, request, uuid):
        # ## cache debe considerar tenant company
        schema_name = schema_name = get_schema_name(request)
        filter_params, page_number, page_size = get_pagination_parameters_rest(
            request)
        filter_params_str_cache_key = get_filter_string(filter_params)
        cache_key = f"{self.service.repository.model.__name__}{schema_name}{filter_params_str_cache_key}{uuid}_one"
        cache_data = self.get_cached_data(cache_key)

        if cache_data:
            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elemento encontrado',
                    'data': cache_data
                },
                status=status.HTTP_200_OK
            )

        try:
            serialized_instance = self.service.find_one_by_uuid(
                uuid, filter_params)
            self.set_cached_data(cache_key, serialized_instance)
            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elemento encontrado',
                    'data': serialized_instance
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return handle_rest_exception_helper(e)


class RetrieveViewMixinNoCache:
    def get(self, request, uuid):
        try:
            serialized_instance = self.service.find_one_by_uuid(uuid)
            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elemento encontrado',
                    'data': serialized_instance
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return handle_rest_exception_helper(e)


# other
class RetrievePkViewMixin(CacheViewMixin):
    def get(self, request, pk):
        # ## cache debe considerar tenant company
        schema_name = get_schema_name(request)
        cache_key = f"{self.service.repository.model.__name__}{schema_name}{pk}_one"
        cache_data = self.get_cached_data(cache_key)

        if cache_data:
            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elemento encontrado',
                    'data': cache_data
                },
                status=status.HTTP_200_OK
            )

        try:
            serialized_instance = self.service.find_one(pk)
            self.set_cached_data(cache_key, serialized_instance)
            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elemento encontrado',
                    'data': serialized_instance
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return handle_rest_exception_helper(e)



# ### NEW VERSION LOGS ES -----------
class UpdateViewMixin(AuditLogMixin, CacheViewMixin):
    def patch(self, request, pk):
        req_data_copy = request.data.copy()
        req_data_copy['custom_user_ixz'] = request.user
        try:
            serialized_instance = self.service.update(pk, req_data_copy)
            pre_snapshot = self._to_dict(self.service.pre_instance) if self.service.pre_instance is not None else {}
            self.audit_update_success_prepost(
                request, serialized_instance, pre_snapshot=pre_snapshot, pk=pk
            )

            self.clear_cache(schema_name=get_schema_name(request))
            return Response(
                {"status": status.HTTP_200_OK, "message": "Elemento actualizado correctamente", "data": serialized_instance},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            self.audit_update_failed(request, e, pk=pk)
            return handle_rest_exception_helper(e)

class UpdateViewNoCacheMixin(AuditLogMixin):
    def patch(self, request, pk):
        try:
            serialized_instance = self.service.update(pk, request.data)

            rid = self._extract_rid(serialized_instance, fallback=pk)
            self._audit_safe(
                request,
                action="UPDATE",
                description="Update OK",
                resource_id=rid,
                extra={"payload_keys": list(request.data.keys())},
            )

            return Response(
                {"status": status.HTTP_200_OK, "message": "Elemento actualizado correctamente", "data": serialized_instance},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            self._audit_safe(
                request,
                action="UPDATE FAILED",
                description=str(e),
                resource_id=pk,
                extra={"payload_keys": list(request.data.keys()), "error": str(e)},
                outcome="FAILED",
            )
            return handle_rest_exception_helper(e)

class DestroyViewMixin(AuditLogMixin, CacheViewMixin):
    def delete(self, request, pk):
        try:
            self.service.delete(pk)

            self._audit_safe(
                request,
                action="DELETE",
                description="Delete OK",
                resource_id=pk,
            )

            self.clear_cache(schema_name=get_schema_name(request))
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            self._audit_safe(
                request,
                action="DELETE FAILED",
                description=str(e),
                resource_id=pk,
                extra={"error": str(e)},
                outcome="FAILED",
            )

# ### Sales Mixins ===================================
class ListViewSalesMixin(CacheViewMixin):
    def get(self, request):
        try:
            filter_params, page_number, page_size = get_pagination_parameters_rest(
                request)
            # ## cache debe considerar el user id para la key xq se filtra por user, role, canal_venta, etc., ademas del schema_name
            cache_key = self.get_cache_key({
                **filter_params, **{'user_id': request.user.id, 'schema_name': get_schema_name(request)}})
            cache_data = self.get_cached_data(cache_key)
            if cache_data:
                return Response(
                    {
                        'status': status.HTTP_200_OK,
                        'message': 'Elementos paginados correctamente',
                        'data': {
                            'meta': cache_data['meta'],
                            'items': cache_data['data'],
                        }
                    },
                    status=status.HTTP_200_OK
                )

            serialized_instances = self.service.find_all(
                filter_params=filter_params, page_number=page_number, page_size=page_size, user_id=request.user.id)
            self.set_cached_data(
                cache_key, {
                    'meta': serialized_instances['meta'], 'data': serialized_instances['data']}
            )

            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elementos paginados correctamente',
                    'data': {
                        'meta': serialized_instances['meta'],
                        'items': serialized_instances['data'],
                    }
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return handle_rest_exception_helper(e)


# UUID
class RetrieveViewSalesMixin(CacheViewMixin):
    def get(self, request, uuid):
        # ## cache debe considerar el user id para la key xq se filtra por user, role, canal_venta, etc.
        cache_key = self.get_cache_key(
            {'user_id': request.user.id, 'model_name': self.service.repository.model.__name__, 'uuid': uuid, 'schema_name': get_schema_name(request)})
        cache_data = self.get_cached_data(cache_key)

        if cache_data:
            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elemento encontrado',
                    'data': cache_data
                },
                status=status.HTTP_200_OK
            )

        try:
            serialized_instance = self.service.find_one_by_uuid(
                uuid=uuid, user_id=request.user.id)
            self.set_cached_data(cache_key, serialized_instance)
            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elemento encontrado',
                    'data': serialized_instance
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return handle_rest_exception_helper(e)



class CreateViewSalesMixin(AuditLogMixin, CacheViewMixin):
    def post(self, request):
        try:
            serialized_instance = self.service.create(request.data, request.user)

            rid = self._extract_rid(serialized_instance)
            self._audit_safe(
                request, action="CREATE", description="Create OK", resource_id=rid,
                extra={"payload_keys": list(request.data.keys()), "context": "SALES"}
            )

            self.clear_cache(schema_name=get_schema_name(request))
            return Response(
                {"status": status.HTTP_201_CREATED, "message": "Elemento creado correctamente", "data": serialized_instance},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            self._audit_safe(
                request, action="CREATE FAILED", description=str(e),
                extra={"payload_keys": list(request.data.keys()), "context": "SALES", "error": str(e)},
                outcome="FAILED"
            )
            return handle_rest_exception_helper(e)

class UpdateViewSalesMixin(AuditLogMixin, CacheViewMixin):
    def patch(self, request, pk):
        try:
            serialized_instance = self.service.update(pk, request.data, request.user)

            rid = self._extract_rid(serialized_instance, fallback=pk)
            self._audit_safe(
                request, action="UPDATE", description="Update OK", resource_id=rid,
                extra={"payload_keys": list(request.data.keys()), "context": "SALES"}
            )

            self.clear_cache(schema_name=get_schema_name(request))
            return Response(
                {"status": status.HTTP_200_OK, "message": "Elemento actualizado correctamente", "data": serialized_instance},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            self._audit_safe(
                request, action="UPDATE FAILED", description=str(e), resource_id=pk,
                extra={"payload_keys": list(request.data.keys()), "context": "SALES", "error": str(e)},
                outcome="FAILED"
            )
            return handle_rest_exception_helper(e)

def get_schema_name(request):
    return request.tenant.company.schema_name if hasattr(request, 'tenant') else env.str('DEFAULT_SCHEMA')


# ## Sales Mixins withouth cache ===================================
class ListViewSalesMixinNoCache:
    def get(self, request):
        try:
            filter_params, page_number, page_size = get_pagination_parameters_rest(
                request)
            serialized_instances = self.service.find_all(
                filter_params=filter_params, page_number=page_number, page_size=page_size, user_id=request.user.id)
            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elementos paginados correctamente',
                    'data': {
                        'meta': serialized_instances['meta'],
                        'items': serialized_instances['data'],
                    }
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return handle_rest_exception_helper(e)


class RetrieveViewSalesMixinNoCache:
    def get(self, request, uuid):
        try:
            serialized_instance = self.service.find_one_by_uuid(
                uuid=uuid, user_id=request.user.id)
            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elemento encontrado',
                    'data': serialized_instance
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return handle_rest_exception_helper(e)


class CreateViewSalesMixinNoCache(AuditLogMixin):
    def post(self, request):
        try:
            serialized_instance = self.service.create(request.data, request.user.id)

            rid = self._extract_rid(serialized_instance)
            self._audit_safe(
                request, action="CREATE", description="Create OK", resource_id=rid,
                extra={"payload_keys": list(request.data.keys()), "context": "SALES"}
            )

            return Response(
                {"status": status.HTTP_201_CREATED, "message": "Elemento creado correctamente", "data": serialized_instance},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            self._audit_safe(
                request, action="CREATE FAILED", description=str(e),
                extra={"payload_keys": list(request.data.keys()), "context": "SALES", "error": str(e)},
                outcome="FAILED"
            )
            return handle_rest_exception_helper(e)

class UpdateViewSalesMixinNoCache(AuditLogMixin):
    def patch(self, request, pk):
        try:
            serialized_instance = self.service.update(pk, request.data, request.user.id)

            rid = self._extract_rid(serialized_instance, fallback=pk)
            self._audit_safe(
                request, action="UPDATE", description="Update OK", resource_id=rid,
                extra={"payload_keys": list(request.data.keys()), "context": "SALES"}
            )

            return Response(
                {"status": status.HTTP_200_OK, "message": "Elemento actualizado correctamente", "data": serialized_instance},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            self._audit_safe(
                request, action="UPDATE FAILED", description=str(e), resource_id=pk,
                extra={"payload_keys": list(request.data.keys()), "context": "SALES", "error": str(e)},
                outcome="FAILED"
            )
            return handle_rest_exception_helper(e)

# ## GENERIC VIEWS ===================================
class FindOneByGenericFiledViewMixin(CacheViewMixin):
    def get_mx(self, request, service_method, field_value, model_name, cache_key=None):
        # ## cache debe considerar tenant company
        schema_name = get_schema_name(request)
        cache_key_x = cache_key if cache_key else f"{model_name}{schema_name}{field_value}__one"
        cache_data = self.get_cached_data(cache_key_x)

        if cache_data:
            print('-------------- CACHE ----------------')
            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elemento encontrado',
                    'data': cache_data
                },
                status=status.HTTP_200_OK
            )

        try:
            serialized_instance = service_method(field_value)
            self.set_cached_data(cache_key_x, serialized_instance)
            print('-------------- DB ----------------')
            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elemento encontrado',
                    'data': serialized_instance
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return handle_rest_exception_helper(e)


class GenericFindOneFieldViewMixinCache(CacheViewMixin):
    def get_mx(self, request, field=None, cache_key=None, model_name=None):
        try:
            filter_params = request.GET

            schema_name = get_schema_name(request)
            cache_key_x_1 = generate_cache_key_generic_one_field(
                field, model_name, schema_name, filter_params)
            cache_key_x = f"{cache_key}_{cache_key_x_1}" if cache_key else cache_key_x_1
            cache_data = self.get_cached_data(cache_key_x)

            if cache_data:
                return Response(
                    {
                        'status': status.HTTP_200_OK,
                        'message': 'Elemento encontrado',
                        'data': cache_data
                    },
                    status=status.HTTP_200_OK
                )

            serialized = self.generic_find_one_field_method(
                request, field, cache_key, model_name, filter_params)
            self.set_cached_data(cache_key_x, serialized)
            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elemento encontrado',
                    'data': serialized
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return handle_rest_exception_helper(e)


class GenericFindOneFieldViewMixinNoCache:
    def get_mx(self, request, field=None, message=None):
        try:
            filter_params = request.GET
            serialized = self.generic_find_one_field_method(
                request, field, None, None, filter_params)
            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': message or 'Elemento encontrado',
                    'data': serialized
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return handle_rest_exception_helper(e)


class FindAllGenericViewMixin(CacheViewMixin):
    def get_mx(self, request, cache_key=None, additional_cache_key=None):
        try:
            opt_key = additional_cache_key if additional_cache_key else ''
            filter_params, page_number, page_size = get_pagination_parameters_rest(
                request)
            # ## cache debe considerar tenant company
            schema_name = get_schema_name(request)
            cache_key_x = cache_key if cache_key else self.get_cache_key({
                **filter_params, **{'schema_name': schema_name}, **{'opt_key': opt_key}
            })
            cache_data = self.get_cached_data(cache_key_x)

            if cache_data:
                return Response(
                    {
                        'status': status.HTTP_200_OK,
                        'message': 'Elementos encontrados correctamente',
                        'data': {
                            'meta': cache_data['meta'],
                            'items': cache_data['data'],
                        }
                    },
                    status=status.HTTP_200_OK
                )

            serialized_instances = self.generic_get_method(
                request, filter_params, page_number, page_size)
            self.set_cached_data(
                cache_key_x, {
                    'meta': serialized_instances['meta'], 'data': serialized_instances['data']}
            )

            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elementos encontrados correctamente',
                    'data': {
                        'meta': serialized_instances['meta'],
                        'items': serialized_instances['data'],
                    }
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return handle_rest_exception_helper(e)


class BaseGenericGETView(CacheViewMixin):
    def get_mx(self, request, service_method, cache_key=None):
        try:
            filter_params, page_number, page_size = get_pagination_parameters_rest(
                request)
            # ## cache debe considerar tenant company
            schema_name = get_schema_name(request)
            cache_key_x = cache_key if cache_key else self.get_cache_key({
                **filter_params, **{'schema_name': schema_name}
            })
            cache_data = self.get_cached_data(cache_key_x)

            if cache_data:
                return Response(
                    {
                        'status': status.HTTP_200_OK,
                        'message': 'Elementos paginados correctamente',
                        'data': {
                            'meta': cache_data['meta'],
                            'items': cache_data['data'],
                        }
                    },
                    status=status.HTTP_200_OK
                )

            serialized_instances = service_method(
                filter_params, page_number, page_size)
            self.set_cached_data(
                cache_key_x, {
                    'meta': serialized_instances['meta'], 'data': serialized_instances['data']}
            )

            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elementos paginados correctamente',
                    'data': {
                        'meta': serialized_instances['meta'],
                        'items': serialized_instances['data'],
                    }
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return handle_rest_exception_helper(e)



class BaseGenericPOSTView(AuditLogMixin, CacheViewMixin):
    def post_mxv(self, request, field=None):
        try:
            serialized = self.generic_post_method(request, field)

            rid = self._extract_rid(serialized)
            self._audit_safe(
                request, action="CREATE", description="Generic POST OK", resource_id=rid,
                extra={"payload_keys": list(request.data.keys()), "generic": True}
            )

            self.clear_cache(schema_name=get_schema_name(request))
            return Response(
                {"status": status.HTTP_201_CREATED, "message": "Elemento creado correctamente", "data": serialized},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            self._audit_safe(
                request, action="CREATE FAILED", description=str(e),
                extra={"payload_keys": list(request.data.keys()), "generic": True, "error": str(e)},
                outcome="FAILED"
            )
            return handle_rest_exception_helper(e)

class BaseGenericPATCHView(AuditLogMixin, CacheViewMixin, ABC):
    @abstractmethod
    def generic_patch_method(self, request, pk, args=None):
        """
        Must be implemented in the child class to handle the patch request
        with custom service method.
        """
        pass

    def patch_mxv(self, request, pk, args=None):
        try:
            sig = inspect.signature(self.generic_patch_method)
            params = list(sig.parameters.keys())
            serialized = self.generic_patch_method(request, pk, args) if len(params) >= 3 else self.generic_patch_method(request, pk)

            rid = self._extract_rid(serialized, fallback=pk)
            self._audit_safe(
                request, action="PATCH", description="Generic PATCH OK", resource_id=rid,
                extra={"payload_keys": list(request.data.keys()), "generic": True, "args": bool(args)}
            )

            self.clear_cache(schema_name=get_schema_name(request))
            extra_data = args.get('extra_data') if args else None
            return Response(
                {
                    'status': args.get('status') if args and args.get('status') else status.HTTP_200_OK,
                    'message': args.get('message') if args else 'Elemento actualizado correctamente',
                    'data': serialized,
                    'extra_data': extra_data if extra_data else None
                },
                status=args.get('status') if args and args.get('status') else status.HTTP_200_OK
            )
        except Exception as e:
            self._audit_safe(
                request, action="PATCH FAILED", description=str(e), resource_id=pk,
                extra={"payload_keys": list(request.data.keys()), "generic": True, "error": str(e)},
                outcome="FAILED"
            )
            return handle_rest_exception_helper(e)

class BaseGenericPATCHCustomFieldView(AuditLogMixin, CacheViewMixin, ABC):
    @abstractmethod
    def generic_patch_method(self, request, field):
        pass

    def patch_mxv(self, request, field):
        try:
            serialized = self.generic_patch_method(request, field)

            rid = self._extract_rid(serialized)
            self._audit_safe(
                request, action="PATCH", description="Generic PATCH Field OK", resource_id=rid,
                extra={"payload_keys": list(request.data.keys()), "field": field}
            )

            self.clear_cache(schema_name=get_schema_name(request))
            return Response(
                {'status': status.HTTP_200_OK, 'message': 'Elemento actualizado correctamente', 'data': serialized},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            self._audit_safe(
                request, action="PATCH FAILED", description=str(e),
                extra={"payload_keys": list(request.data.keys()), "field": field, "error": str(e)},
                outcome="FAILED"
            )
            return handle_rest_exception_helper(e)

# ### Generic User Views ===========================================
class ListViewUserMixin(CacheViewMixin):
    def get(self, request):
        try:
            filter_params, page_number, page_size = get_pagination_parameters_rest(
                request)
            # ## cache debe considerar el user id para la key.
            cache_key = self.get_cache_key({
                **filter_params, **{'user_id': request.user.id, 'schema_name': get_schema_name(request)}})
            cache_data = self.get_cached_data(cache_key)
            if cache_data:
                print('-------------- [GENERIC USER]: CACHE ----------------')
                return Response(
                    {
                        'status': status.HTTP_200_OK,
                        'message': 'Elementos encontrados',
                        'data': {
                            'meta': cache_data['meta'],
                            'items': cache_data['data'],
                        }
                    },
                    status=status.HTTP_200_OK
                )

            serialized_instances = self.service.find_all(
                filter_params=filter_params, page_number=page_number, page_size=page_size, user_id=request.user.id, user_x=request.user)
            self.set_cached_data(
                cache_key, {
                    'meta': serialized_instances['meta'], 'data': serialized_instances['data']}
            )

            print('-------------- [GENERIC USER]: DB ----------------')
            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elementos encontrados',
                    'data': {
                        'meta': serialized_instances['meta'],
                        'items': serialized_instances['data'],
                    }
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return handle_rest_exception_helper(e)


# UUID
class RetrieveViewUserMixin(CacheViewMixin):
    def get(self, request, uuid):
        # ## cache debe considerar el user id para la key.
        cache_key = self.get_cache_key(
            {'user_id': request.user.id, 'model_name': self.service.repository.model.__name__, 'uuid': uuid, 'schema_name': get_schema_name(request)})
        cache_data = self.get_cached_data(cache_key)

        if cache_data:
            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elemento encontrado',
                    'data': cache_data
                },
                status=status.HTTP_200_OK
            )

        try:
            serialized_instance = self.service.find_one_by_uuid(
                uuid=uuid, user_id=request.user.id)
            self.set_cached_data(cache_key, serialized_instance)
            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elemento encontrado',
                    'data': serialized_instance
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return handle_rest_exception_helper(e)


class CreateViewUserMixin(AuditLogMixin, CacheViewMixin):
    def post(self, request):
        try:
            serialized_instance = self.service.create(request.data, request.user)

            rid = self._extract_rid(serialized_instance)
            self._audit_safe(
                request, action="CREATE", description="Create OK", resource_id=rid,
                extra={"payload_keys": list(request.data.keys()), "context": "USER"}
            )

            self.clear_cache(schema_name=get_schema_name(request))
            return Response(
                {"status": status.HTTP_201_CREATED, "message": "Elemento creado correctamente", "data": serialized_instance},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            self._audit_safe(
                request, action="CREATE FAILED", description=str(e),
                extra={"payload_keys": list(request.data.keys()), "context": "USER", "error": str(e)},
                outcome="FAILED"
            )
            return handle_rest_exception_helper(e)

class UpdateViewUserMixin(AuditLogMixin, CacheViewMixin):
    def patch(self, request, pk):
        try:
            serialized_instance = self.service.update(pk, request.data, request.user)

            rid = self._extract_rid(serialized_instance, fallback=pk)
            self._audit_safe(
                request, action="UPDATE", description="Update OK", resource_id=rid,
                extra={"payload_keys": list(request.data.keys()), "context": "USER"}
            )

            self.clear_cache(schema_name=get_schema_name(request))
            return Response(
                {"status": status.HTTP_200_OK, "message": "Elemento actualizado correctamente", "data": serialized_instance},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            self._audit_safe(
                request, action="UPDATE FAILED", description=str(e), resource_id=pk,
                extra={"payload_keys": list(request.data.keys()), "context": "USER", "error": str(e)},
                outcome="FAILED"
            )
            return handle_rest_exception_helper(e)

# Generic User Views withouth cache ---------------
class ListViewUserMixinNoCache:
    def get(self, request):
        try:
            filter_params, page_number, page_size = get_pagination_parameters_rest(
                request)
            serialized_instances = self.service.find_all(
                filter_params=filter_params, page_number=page_number, page_size=page_size, user_id=request.user.id)
            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elementos encontrados',
                    'data': {
                        'meta': serialized_instances['meta'],
                        'items': serialized_instances['data'],
                    }
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return handle_rest_exception_helper(e)


class RetrieveViewUserMixinNoCache:
    def get(self, request, uuid):
        try:
            serialized_instance = self.service.find_one_by_uuid(
                uuid=uuid, user_id=request.user.id)
            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elemento encontrado',
                    'data': serialized_instance
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return handle_rest_exception_helper(e)



class CreateViewUserMixinNoCache(AuditLogMixin):
    def post(self, request):
        try:
            serialized_instance = self.service.create(request.data, request.user.id)

            rid = self._extract_rid(serialized_instance)
            self._audit_safe(
                request, action="CREATE", description="Create OK", resource_id=rid,
                extra={"payload_keys": list(request.data.keys()), "context": "USER"}
            )

            return Response(
                {"status": status.HTTP_201_CREATED, "message": "Elemento creado correctamente", "data": serialized_instance},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            self._audit_safe(
                request, action="CREATE FAILED", description=str(e),
                extra={"payload_keys": list(request.data.keys()), "context": "USER", "error": str(e)},
                outcome="FAILED"
            )
            return handle_rest_exception_helper(e)

class UpdateViewUserMixinNoCache(AuditLogMixin):
    def patch(self, request, pk):
        try:
            serialized_instance = self.service.update(pk, request.data, request.user.id)

            rid = self._extract_rid(serialized_instance, fallback=pk)
            self._audit_safe(
                request, action="UPDATE", description="Update OK", resource_id=rid,
                extra={"payload_keys": list(request.data.keys()), "context": "USER"}
            )

            return Response(
                {"status": status.HTTP_200_OK, "message": "Elemento actualizado correctamente", "data": serialized_instance},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            self._audit_safe(
                request, action="UPDATE FAILED", description=str(e), resource_id=pk,
                extra={"payload_keys": list(request.data.keys()), "context": "USER", "error": str(e)},
                outcome="FAILED"
            )
            return handle_rest_exception_helper(e)


# ### Generic General Views NO repos,services, no normal structure ===========================================
class ListViewGenericNoPagingNoStructureMixin:
    def get(self, request):
        try:
            # cache
            schema_name = get_schema_name(request)

            # must be defined in the child class
            cache_custom_name_part = self.cache_name_part or ''
            cache_key = f"{schema_name}_{cache_custom_name_part}_all"
            cache_data = cache.get(cache_key)

            if cache_data:
                return Response(
                    {
                        'status': status.HTTP_200_OK,
                        'message': 'Elementos encontrados',
                        'data': cache_data
                    },
                    status=status.HTTP_200_OK
                )

            # must be defined in the child class
            serialized_instances = self.generic_find_all_method(request)
            cache.set(cache_key, {
                'meta': None, 'items': serialized_instances})

            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elementos encontrados',
                    'data': {
                        'meta': None,
                        'items': serialized_instances
                    }
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return handle_rest_exception_helper(e)


# ### CUSTOM GENERIC METHODS NO CACHE ===========================================
class BaseGenericGETALLNoCacheViewMixin():
    def get_mxv(self, request, success_message=None, success_status=None):
        try:
            filter_params, page_number, page_size = get_pagination_parameters_rest(
                request)
            # must be defined in the child class
            serialized_paginated_data = self.generic_get_method(
                request, filter_params, page_number, page_size)
            return Response(
                {
                    'status': success_status or status.HTTP_200_OK,
                    'message': success_message or 'Elementos encontrados correctamente',
                    'data': {
                        'meta': serialized_paginated_data['meta'],
                        'items': serialized_paginated_data['data'],
                    }
                },
                status=success_status or status.HTTP_200_OK
            )
        except Exception as e:
            return handle_rest_exception_helper(e)


class BaseGenericGETNoCacheView():
    def get_mxv(self, request, success_message=None, success_status=None):
        try:
            # must be defined in the child class
            serialized_data = self.generic_get_method(request)
            return Response(
                {
                    'status': success_status or status.HTTP_200_OK,
                    'message': success_message or 'Elemento encontrado',
                    'data': serialized_data
                },
                status=success_status or status.HTTP_200_OK
            )
        except Exception as e:
            return handle_rest_exception_helper(e)



class BaseGenericPOSTNoCacheView(AuditLogMixin):
    def post_mxv(self, request, success_message=None, success_status=None):
        try:
            serialized_instance = self.generic_post_method(request)

            rid = self._extract_rid(serialized_instance)
            self._audit_safe(
                request, action="CREATE", description="Generic POST NoCache OK", resource_id=rid,
                extra={"payload_keys": list(request.data.keys()), "nocache": True}
            )

            return Response(
                {
                    'status': success_status or status.HTTP_201_CREATED,
                    'message': success_message or 'Elemento creado correctamente',
                    'data': serialized_instance
                },
                status=success_status or status.HTTP_201_CREATED
            )
        except Exception as e:
            self._audit_safe(
                request, action="CREATE FAILED", description=str(e),
                extra={"payload_keys": list(request.data.keys()), "nocache": True, "error": str(e)},
                outcome="FAILED"
            )
            return handle_rest_exception_helper(e)
