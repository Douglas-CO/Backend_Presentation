from typing import Type
from django.contrib.auth.models import Permission

from config.shared.repositories.base_repository import BaseRepositoryAllMixin

from users.models.custom_group_model import CustomGroup


class CustomGroupRepository(BaseRepositoryAllMixin):
    model: Type[CustomGroup]

    def __init__(self, model):
        super().__init__(model)

    def create(self, data) -> object:
        permissions_codename_list = data.pop('permissions', [])
        group = self.model.objects.create(**data)

        if permissions_codename_list:
            permissions = self.find_all_permissions_by_codename_list(
                permissions_codename_list)
            permissions = [p.id for p in permissions]
            group.permissions.set(permissions)
        return group

    def update(self, instance_id, data) -> object:
        permissions_codename_list = data.pop(
            'permissions') if 'permissions' in data else None
        group = self.find_one(instance_id)
        for attr, value in data.items():
            setattr(group, attr, value)
        group.save()

        permissions = self.find_all_permissions_by_codename_list(
            permissions_codename_list) if permissions_codename_list else None
        permissions = [p.id for p in permissions] if permissions else None

        if permissions is None:
            return group
        if len(permissions) == 0:
            group.permissions.clear()
            return group
        group.permissions.set(permissions)
        return group

    def find_all_permissions_by_codename_list(self, codename_list) -> list[Permission]:
        return Permission.objects.filter(codename__in=codename_list)
