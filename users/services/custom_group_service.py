from django.db import transaction

from config.shared.services.base_service import BaseServiceAllMixin
from config.shared.exceptions.bad_request_exception import BadRequestException

from users.repositories.custom_group_repository import CustomGroupRepository
from users.filters.custom_group_filters import CustomGroupFilter
from users.serializers.custom_group_serializers import (
    CustomGroupSerializer,
    CustomGroupResponseSerializer,
)
from users.models.usuario_model import Usuario
from config.shared.services.base_mixins_service import CacheServiceMixin
from config.shared.exceptions.resource_not_found_exception import ResourceNotFoundException


class CustomGroupService(BaseServiceAllMixin, CacheServiceMixin):
    repository: CustomGroupRepository

    filter = CustomGroupFilter

    serializer = CustomGroupSerializer
    serializer2 = CustomGroupResponseSerializer

    def __init__(self, repository):
        super().__init__(repository, filter=self.filter,
                         serializer=self.serializer, serializer2=self.serializer2)

    @transaction.atomic
    def create(self, data):
        return super().create_mx(data)

    def find_user_by_group_code(self, group_code, user_id) -> Usuario:
        user = Usuario.objects.filter(
            pk=user_id,
            state=True
        ).first()
        if not user:
            raise BadRequestException('El usuario no existe o no está activo')
        user_groups = user.groups.all()
        custom_group = self.repository.find_one_by_attrs({
            'codigo': group_code
        })
        user_groups_str_comma = ', '.join(
            [group.name for group in user_groups])
        user_name = user.razon_social

        custom_group_id = custom_group.id
        if custom_group_id not in [group.id for group in user_groups]:
            raise BadRequestException(
                f'El usuario no tiene el rol de vendedor asignado, rol actual: {user_groups_str_comma}, nombre del usuario: {user_name}')

        return user

    @transaction.atomic
    def update(self, pk, data):
        return super().update_mx(pk, data)

    def update_extension_method(self, validated_data, raw_data=None, pk=None, instance=None):
        self.clear_all_model_cache(
            model_name=self.repository.model.__name__)

    # ----------------
    def find_all_by_pk_list_qs(self, pk_list):
        not_fount = []
        custom_groups_qs = self.repository.find_all_by_pk_list(pk_list)

        # validar la cantidad de elementos q pide y las q trae
        if len(pk_list) != len(custom_groups_qs):
            not_fount = list(
                set(pk_list) - set([r.id for r in custom_groups_qs]))

        if not_fount:
            raise ResourceNotFoundException(
                f'No se encontraron los siguientes ids: {not_fount}')

        return custom_groups_qs
