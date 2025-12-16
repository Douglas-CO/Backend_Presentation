from typing import Type

from config.shared.services.base_service import BaseServiceMixin

from log.repositories.role_repositories import RoleRepository
from log.filters.role_filters import RoleFilter
from log.serializers.role_serializers import (
    RoleSerializer,
    RoleResponseSerializer,
)


class RoleService(BaseServiceMixin):
    repository: Type[RoleRepository]

    filter = Type[RoleFilter]

    serializer = Type[RoleSerializer]
    serializer2 = Type[RoleResponseSerializer]

    def __init__(self, repository):
        filter = RoleFilter
        serializer = RoleSerializer
        serializer2 = RoleResponseSerializer
        super().__init__(repository, filter, serializer, serializer2)
