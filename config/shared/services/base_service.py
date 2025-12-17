from config.shared.constants.constants import (
    PAGINATION_DEFAULT_PAGE_NUMBER,
    PAGINATION_DEFAULT_PAGE_SIZE,
)
from config.shared.exceptions.resource_not_found_exception import ResourceNotFoundException
from config.shared.utils.common_utils import humanize_model_name, format_params

# ## Service Mixins -----------------------
from config.shared.services.base_mixins_service import PaginationServiceMixin, SerializationServiceMixin, FindServiceMixin, UpdateServiceMixin, CreateServiceInstanceMixin


class BaseServiceMixin(PaginationServiceMixin, SerializationServiceMixin, FindServiceMixin, CreateServiceInstanceMixin, UpdateServiceMixin):
    # DI: inject the repository | other just args
    def __init__(self, repository, filter=None, serializer=None, serializer2=None, serializer_upd=None):
        self.repository = repository
        self.filter = filter
        self.serializer = serializer
        self.serializer2 = serializer2
        self.serializer_upd = serializer_upd

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

    def find_one_uuid_post_serializer(self, serialized_data, instance, filter_params=None):
        """
        This method is used to extend the serialized data after the serialization process when finding one instance by UUID. You must return the serialized data, even if you don't modify it.
        """
        return serialized_data

    def update_extension_method(self, validated_data, raw_data=None, pk=None, instance=None) -> bool | None:
        """
        This method is used to extend the update logic. If you want to update using the repository, you must return None, otherwise return true to handle the update&serializer, in the service.
        """
        return None

    def create_extension_method(self, validated_data, raw_data=None):
        """
        This method is used to extend the create logic. If you want to create using the repository, you must return None, otherwise return true to handle the create&serializer in the service
        """
        return None

    # ### MAIN methods ===========================
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

    def find_one(self, pk) -> dict:
        instance = self.find_one_mx(pk)
        return self.serialize(instance)

    def find_one_by_uuid(self, uuid, filter_params=None) -> dict:
        instance = self.find_one_by_uuid_mx(uuid)
        serialized_x = self.serialize(instance)
        serialized_y = self.find_one_uuid_post_serializer(
            serialized_x, instance, filter_params)
        return serialized_y

    def find_one_by_attr(self, attr: str, value) -> dict:
        instance = self.find_one_by_attr_mx(attr, value)
        return self.serialize(instance)

    def create(self, data) -> dict:
        return self.create_mx(data)

    def create_i(self, data):
        return self.create_mx_i(data)

    def update(self, pk, data) -> dict:
        return self.update_mx(pk, data)

    def find_one_instance(self, pk):
        instance = self.repository.find_one(pk)
        humanized_model_name = humanize_model_name(
            self.repository.model.__name__)
        if instance is None:
            raise ResourceNotFoundException(
                f'{humanized_model_name} con id {pk} no encontrado')
        return instance

    def find_one_active_instance(self, pk):
        instance = self.repository.find_one(pk)
        humanized_model_name = humanize_model_name(
            self.repository.model.__name__)
        if instance is None:
            raise ResourceNotFoundException(
                f'{humanized_model_name} con id {pk} no encontrado')
        if hasattr(instance, 'state') and not instance.state:
            raise ResourceNotFoundException(
                f"{humanized_model_name} con id {pk} no se encuentra activo"
            )

        return instance

    def find_one_instance_by_attrs(self, params: dict):
        instance = self.repository.find_one_by_attrs(params)
        if instance is None:
            humanized_model_name = humanize_model_name(
                self.repository.model.__name__)
            formatted_params = format_params(params)
            raise ResourceNotFoundException(
                f"{humanized_model_name} con {formatted_params} no encontrado"
            )
        return instance

    def find_one_instance_by_attrs_qs(self, params: dict):
        queryset = self.repository.find_one_by_attrs_qs(params)
        if queryset is None:
            humanized_model_name = humanize_model_name(
                self.repository.model.__name__)
            formatted_params = format_params(params)
            raise ResourceNotFoundException(
                f"{humanized_model_name} con {formatted_params} no encontrado"
            )
        return queryset
