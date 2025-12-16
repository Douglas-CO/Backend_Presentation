from typing import Type

from log.models.role_model import Role
from config.shared.repositories.base_repository import BaseRepositoryMixin

class RoleRepository(BaseRepositoryMixin):
    model: Type[Role]

    def __init__(self, model):
        super().__init__(model)
