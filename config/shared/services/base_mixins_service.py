from django.core.cache import cache

from config.shared.exceptions.resource_not_found_exception import ResourceNotFoundException
from config.shared.exceptions.invalid_fields_exception import InvalidFieldsException
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from config.shared.constants.constants import PAGINATION_DEFAULT_PAGE_NUMBER, PAGINATION_DEFAULT_PAGE_SIZE
from config.shared.utils.common_utils import humanize_model_name


class SafePaginationMixin:
    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 30

    @staticmethod
    def paginate_queryset(queryset, page_number=None, page_size=None):
        try:
            page_number = int(
                page_number) if page_number is not None else SafePaginationMixin.DEFAULT_PAGE
        except (TypeError, ValueError):
            page_number = SafePaginationMixin.DEFAULT_PAGE

        try:
            page_size = int(
                page_size) if page_size is not None else SafePaginationMixin.DEFAULT_PAGE_SIZE
        except (TypeError, ValueError):
            page_size = SafePaginationMixin.DEFAULT_PAGE_SIZE

        if page_number < 1:
            page_number = SafePaginationMixin.DEFAULT_PAGE
        if page_size < 1:
            page_size = SafePaginationMixin.DEFAULT_PAGE_SIZE
        if page_size > SafePaginationMixin.MAX_PAGE_SIZE:
            page_size = SafePaginationMixin.MAX_PAGE_SIZE

        paginator = Paginator(queryset, page_size)

        if paginator.num_pages > 0 and page_number > paginator.num_pages:
            page_obj = []
            next_page = previous_page = None
        else:
            try:
                page_obj = paginator.page(page_number)
            except (PageNotAnInteger, EmptyPage):
                page_number = 1
                page_obj = paginator.page(1)

            next_page = page_obj.next_page_number() if hasattr(
                page_obj, "has_next") and page_obj.has_next() else None
            previous_page = page_obj.previous_page_number() if hasattr(
                page_obj, "has_previous") and page_obj.has_previous() else None

        return {
            "page_obj": page_obj,
            "next_page": next_page,
            "previous_page": previous_page,
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "page": page_number,
            "page_size": page_size,
        }


class PaginationServiceMixin:
    def paginate_queryset(
            self,
            queryset,
            page_number=PAGINATION_DEFAULT_PAGE_NUMBER,
            page_size=PAGINATION_DEFAULT_PAGE_SIZE
    ):
        paginator = Paginator(queryset, page_size)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = []

        if isinstance(page_obj, list):
            next_page = previous_page = None
            count = total_pages = 0
        else:
            next_page = page_obj.next_page_number() if page_obj.has_next() else None
            previous_page = page_obj.previous_page_number() if page_obj.has_previous() else None
            count = paginator.count
            total_pages = paginator.num_pages

        return {
            "page_obj": page_obj,
            "next_page": next_page,
            "previous_page": previous_page,
            "count": count,
            "total_pages": total_pages,
        }


class SerializationServiceMixin:
    serializer = None  # model serializer
    serializer2 = None  # response
    serializer_upd = None  # update

    def serialize(self, instance, many=False):
        if self.serializer2:
            return self.serializer2(instance, many=many).data
        raise NotImplementedError("serializer2 not defined")

    def validate_and_serialize(self, data):
        serializer = self.serializer(data=data)
        if serializer.is_valid():
            return serializer.validated_data
        # error_fileds_msg_str = serializer.errors.items()
        # error_fileds_msg_str = [
        #     f"{key}: {value}" for key, value in serializer.errors.items()]
        # error_fileds_msg_str = ", ".join(error_fileds_msg_str)
        raise InvalidFieldsException(
            # message=error_fileds_msg_str,
            message="Campo(s) inválido(s)",
            fields=serializer.errors.items()
        )

    def validate_and_serialize_upd(self, instance, data):
        serializer_to_be_used = self.serializer_upd or self.serializer
        serializer = serializer_to_be_used(instance, data=data, partial=True)
        if serializer.is_valid():
            return serializer.validated_data
        raise InvalidFieldsException(
            message="Bad Request", fields=serializer.errors.items()
        )

    def validate_and_serialize_by_serializer(self, data, serializer):
        serialized = serializer(data=data)
        if serialized.is_valid():
            return serialized.validated_data
        raise InvalidFieldsException(
            message="Bad Request", fields=serialized.errors.items()
        )

    def serialize_by_serializer(self, instance, serializer, many=False):
        if serializer:
            return serializer(instance, many=many).data
        raise NotImplementedError("serializer not defined")


class FindServiceMixin:
    def find_all_mx(self, filter=None, filter_params=None, order_by='id', order_by_direction='-'):
        queryset = self.repository.find_all()
        if filter_params:
            queryset = filter(filter_params, queryset=queryset).qs
            order_by = filter_params.get("order_by") or "id"
            order_by_direction = '' if filter_params.get(
                "order_by_asc") else '-'
        order_by_query = f"{order_by_direction}{order_by}"
        queryset = queryset.order_by(order_by_query)
        return queryset

    def find_one_mx(self, pk):
        instance = self.repository.find_one(pk)
        if not instance:
            raise ResourceNotFoundException(
                message=f"Resource {self.repository.model.__name__} con id'{pk}' no encontrado"
            )
        if hasattr(instance, 'state') and not instance.state:
            raise ResourceNotFoundException(
                message=f"El recurso {self.repository.model.__name__} con id '{pk}' está inactivo"
            )
        return instance

    def find_one_by_uuid_mx(self, uuid):
        instance = self.repository.find_one_by_uuid(uuid)
        if not instance:
            raise ResourceNotFoundException(
                message=f"Recurso {self.repository.model.__name__} con '{uuid}' no encontrado"
            )
        if hasattr(instance, 'state') and not instance.state:
            raise ResourceNotFoundException(
                message=f"El recurso {self.repository.model.__name__} con uuid '{uuid}' está inactivo"
            )
        return instance

    def find_one_by_attr_mx(self, attr, value):
        instance = self.repository.find_one_by_attr(attr, value)
        if not instance:
            raise ResourceNotFoundException(
                message=f"Recurso {self.repository.model.__name__} con {attr} '{value}' no encontrado"
            )
        if hasattr(instance, 'state') and not instance.state:
            raise ResourceNotFoundException(
                message=f"El recurso {self.repository.model.__name__} con {attr} '{value}' está inactivo"
            )
        return instance


class CreateServiceInstanceMixin:
    def create_mx_i(self, data):
        validated_data = self.validate_and_serialize(data)

        custom_data = self.create_extension_method(validated_data, data)
        if custom_data:
            return custom_data

        model_instance = self.repository.create(validated_data)
        return model_instance


class UpdateServiceMixin:
    pre_instance = None

    def update_mx(self, pk, data):
        # repeat logic 'cause some mixins find_one (service) error in args:
        instance = self.repository.find_one(pk)
        self.pre_instance = instance.__dict__.copy() if instance else None
        if not instance:
            raise ResourceNotFoundException(
                message=f"Resource with id '{pk}' not found"
            )
        validated_data = self.validate_and_serialize_upd(instance, data)

        custom_serialized = self.update_extension_method(
            validated_data, data, pk, instance)
        if custom_serialized:
            return custom_serialized

        updated_instance = self.repository.update(pk, validated_data)
        return self.serialize(updated_instance)


class DeleteServiceMixin:
    def delete_mx(self, pk):
        was_deleted = self.repository.delete(pk)
        if not was_deleted:
            raise ResourceNotFoundException(
                message=f"Resource with id '{pk}' not found"
            )
        return was_deleted


# ### Another Mixins ===================================
class CacheServiceMixin:
    def clear_all_model_cache(self, model_name: str):
        cache.delete_pattern(f"*{model_name}*")

    def clear_all_schema_cache(self):
        cache.clear()

    def clear_all_model_list(self, name_list: list):
        for name in name_list:
            cache.delete_pattern(f"*{name}*")


# ### Sales Mixins ===================================
# all models must inject user_repository
class FindServiceSalesFilterMixin:
    def find_all_mx(self, filter=None, filter_params=None, order_by='id', order_by_direction='-', user_id=int):
        user = self.user_repository.find_one(user_id)
        if not user:
            raise ResourceNotFoundException(
                message=f"Recurso con id '{user_id}' no encontrado"
            )
        # print('------------- is_superuser:', user.is_superuser, '-------------')

        # step 1: general queryset
        queryset = self.repository.find_all()
        if filter_params:
            queryset = filter(filter_params, queryset=queryset).qs
            order_by = filter_params.get("order_by") or "id"
            order_by_direction = '' if filter_params.get(
                "order_by_asc") else '-'
        order_by_query = f"{order_by_direction}{order_by}"
        queryset = queryset.order_by(order_by_query)

        # step 2: filter by empresa,area,depa,canal_venta,role,user,...
        queryset = self._filter_by_sales_logic_mx(
            queryset, user
        )

        return queryset

    def find_one_mx(self, pk, user_id):
        user = self.user_repository.find_one(user_id)
        if not user:
            raise ResourceNotFoundException(
                message=f"Usuario con id '{user_id}' no encontrado"
            )

        queryset = self.repository.find_one_qs(pk)
        queryset = self._filter_by_sales_logic_mx(
            queryset, user
        )
        instance = queryset.first()
        if not instance:
            raise ResourceNotFoundException(
                message=f"Recurso con id '{pk}' no encontrado"
            )

        return instance

    def find_one_by_uuid_mx(self, uuid, user_id):
        user = self.user_repository.find_one(user_id)
        if not user:
            raise ResourceNotFoundException(
                message=f"Usuario con id '{user_id}' no encontrado"
            )
        # print('------------- is_superuser UUID:', user.is_superuser, '-------------')

        queryset = self.repository.find_all()
        queryset = self._filter_by_sales_logic_mx(
            queryset, user
        )
        instance = queryset.filter(uuid=uuid).first()
        if not instance:
            raise ResourceNotFoundException(
                message=f"Recurso con id '{uuid}' no encontrado"
            )

        return instance

    def find_one_by_attr_mx(self, attr, value, user_id):
        user = self.user_repository.find_one(user_id)
        if not user:
            raise ResourceNotFoundException(
                message=f"Usuario con id '{user_id}' no encontrado"
            )

        queryset = self.repository.find_all()
        queryset = self._filter_by_sales_logic_mx(
            queryset, user
        )
        instance = queryset.filter(**{attr: value}).first()
        if not instance:
            raise ResourceNotFoundException(
                message=f"Recurso con {attr} '{value}' no encontrado"
            )

        return instance

    def _filter_by_sales_logic_mx(self, queryset, user):
        is_superuser = user.is_superuser
        if is_superuser or user.role == 'GERENCIA':
            return queryset

        # TODO: validate this filter logic with actual gerencia
        if hasattr(self.repository.model, 'area') and user.role == 'ADMINISTRADOR':
            queryset = queryset.filter(area=user.area)
        elif hasattr(self.repository.model, 'departamento') and user.role == 'COORDINADOR':
            queryset = queryset.filter(
                departamento=user.departamento)
        elif hasattr(self.repository.model, 'canal_venta') and user.role == 'SUPERVISOR':
            queryset = queryset.filter(
                canal_venta=user.canal_venta)
        elif hasattr(self.repository.model, 'vendedor') and user.role == 'AGENTE':
            queryset = queryset.filter(vendedor=user)

        # tecnico - flota user
        elif hasattr(self.repository.model, 'usuario_flota') and user.role == 'TECNICO':
            queryset = queryset.filter(usuario_flota=user)

        return queryset

    # filter tecnicos by flota user
    def _filter_by_flota_user(self, queryset, flota_user=None):
        if hasattr(self.repository.model, 'usuario_flota'):
            if flota_user:
                queryset = queryset.filter(usuario_flota=flota_user)
        return queryset


class UpdateServiceSalesMixin:
    pre_instance = None

    def update_mx(self, pk, data, user):
        instance = self.repository.find_one(pk)
        if not instance:
            raise ResourceNotFoundException(
                message=f"Recurso con id '{pk}' no encontrado"
            )
        self.pre_instance = instance.__dict__.copy() if instance else None

        validated_data = self.validate_and_serialize_upd(instance, data)

        custom_serialized = self.update_extension_method(
            validated_data, data, pk, instance, user)
        if custom_serialized:
            return custom_serialized

        # # prevent upd area,depa,canal_venta,vendedor:
        # validated_data.pop('area', None)
        # validated_data.pop('departamento', None)
        # validated_data.pop('canal_venta', None)
        # validated_data.pop('vendedor', None)

        updated_instance = self.repository.update(pk, validated_data)
        return self.serialize(updated_instance)


class UserValidatorMixin:
    def find_active_user_instance(self, user_id):
        user = self.user_repository.find_one(user_id)
        if not user:
            raise ResourceNotFoundException(
                message=f"Usuario con id '{user_id}' no encontrado"
            )
        if not user.state:
            raise ResourceNotFoundException(
                message=f"Usuario con id '{user_id}' inactivo"
            )
        return user


# ### Generic User Mixins ===================================
# all models must inject user_repository
class FindServiceGenericUserFilterMixin:
    def find_all_mx(self, filter=None, filter_params=None, order_by='id', order_by_direction='-', user_id=int, ignorar_user=False):
        user = None
        if not ignorar_user:
            user = UserValidatorMixin.find_active_user_instance(self, user_id)
        # print('------------- is_superuser:', user.is_superuser, '-------------')

        # step 1: general queryset
        queryset = self.repository.find_all()
        if filter_params:
            queryset = filter(filter_params, queryset=queryset).qs
            order_by = filter_params.get("order_by") or "id"
            order_by_direction = '' if filter_params.get(
                "order_by_asc") else '-'
        order_by_query = f"{order_by_direction}{order_by}"
        queryset = queryset.order_by(order_by_query)

        # step 2: filter by user logic
        if not ignorar_user:
            queryset = self._filter_by_user_logic_mx(
                queryset, user
            )

        return queryset

    def find_one_mx(self, pk, user_id):
        user = UserValidatorMixin.find_active_user_instance(self, user_id)
        if not user:
            raise ResourceNotFoundException(
                message=f"Usuario con id '{user_id}' no existe o está inactivo")

        queryset = self.repository.find_one_qs(pk)
        queryset = self._filter_by_user_logic_mx(
            queryset, user
        )
        instance = queryset.first()
        if not instance:
            humanized_model_name = humanize_model_name(
                self.repository.model.__name__)
            raise ResourceNotFoundException(
                message=f"{humanized_model_name} con id '{pk}' no encontrado"
            )

        return instance

    def find_one_by_uuid_mx(self, uuid, user_id):
        user = UserValidatorMixin.find_active_user_instance(self, user_id)
        if not user:
            raise ResourceNotFoundException(
                message=f"Usuario con id '{user_id}' no existe o está inactivo")

        queryset = self.repository.find_one_by_uuid_qs(uuid)
        queryset = self._filter_by_user_logic_mx(
            queryset, user
        )
        instance = queryset.first()
        if not instance:
            humanized_model_name = humanize_model_name(
                self.repository.model.__name__)
            raise ResourceNotFoundException(
                message=f"{humanized_model_name} con uuid '{uuid}' no encontrado"
            )

        return instance

    def find_one_by_attr_mx(self, attr, value, user_id):
        user = UserValidatorMixin.find_active_user_instance(self, user_id)
        if not user:
            raise ResourceNotFoundException(
                message=f"Usuario con id '{user_id}' no existe o está inactivo")

        queryset = self.repository.find_one_by_attr_qs(attr, value)
        queryset = self._filter_by_user_logic_mx(
            queryset, user
        )
        instance = queryset.first()
        if not instance:
            humanized_model_name = humanize_model_name(
                self.repository.model.__name__)
            raise ResourceNotFoundException(
                message=f"{humanized_model_name} con {attr} '{value}' no encontrado"
            )

        return instance

    # helper methods -------------
    def _filter_by_user_logic_mx(self, queryset, user):
        is_superuser = user.is_superuser
        if is_superuser or user.role == 'GERENCIA':
            return queryset

        # TODO: validate this filter logic with actual gerencia
        if hasattr(self.repository.model, 'area') and user.role == 'ADMINISTRADOR':
            queryset = queryset.filter(area=user.area)
        elif hasattr(self.repository.model, 'departamento') and user.role == 'COORDINADOR':
            queryset = queryset.filter(
                departamento=user.departamento)
        elif hasattr(self.repository.model, 'canal_venta') and user.role == 'SUPERVISOR':
            queryset = queryset.filter(
                canal_venta=user.canal_venta)
        elif hasattr(self.repository.model, 'vendedor') and user.role == 'AGENTE':
            queryset = queryset.filter(vendedor=user)

        # tecnico - flota user
        elif hasattr(self.repository.model, 'usuario_flota') and user.role == 'TECNICO':
            queryset = queryset.filter(usuario_flota=user)

        return queryset


class CreateServiceGenericUserMixinOld:
    def create_mx(self, data, user_id):
        user = UserValidatorMixin.find_active_user_instance(self, user_id)

        validated_data = self.validate_and_serialize(data)

        serialized_data = self.create_extension_method(
            validated_data, data, user)
        if serialized_data:
            return serialized_data

        saved_i = self.repository.create({
            **validated_data,
        })
        if hasattr(saved_i, 'user_create'):
            saved_i.user_create = user
            saved_i.save()

        return self.serialize(saved_i)


class CreateServiceInstanceGenericUserMixin:
    def create_mx_i(self, data, user_id):
        user = UserValidatorMixin.find_active_user_instance(self, user_id)

        validated_data = self.validate_and_serialize(data)

        serialized_data = self.create_extension_method(
            validated_data, data, user)
        if serialized_data:
            return serialized_data

        saved_i = self.repository.create({
            **validated_data,
        })
        return saved_i


class CreateServiceInstanceGenericUserNoUserMixin:
    def create_mx_i_nouser(self, data):
        validated_data = self.validate_and_serialize(data)

        serialized_data = self.create_extension_method(
            validated_data, data)
        if serialized_data:
            return serialized_data

        saved_i = self.repository.create(validated_data)
        return saved_i


class UpdateServiceGenericUserMixinOld:
    def update_mx(self, pk, data, user_id):
        user = UserValidatorMixin.find_active_user_instance(self, user_id)

        instance = self.repository.find_one(pk)
        if not instance:
            humanized_model_name = humanize_model_name(
                self.repository.model.__name__)
            raise ResourceNotFoundException(
                message=f"{humanized_model_name} con id '{pk}' no encontrado")

        validated_data = self.validate_and_serialize_upd(instance, data)

        custom_serialized = self.update_extension_method(
            validated_data, data, pk, instance, user)
        if custom_serialized:
            return custom_serialized

        updated_i = self.repository.update(pk, validated_data)
        return self.serialize(updated_i)
