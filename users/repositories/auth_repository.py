from django.contrib.auth.models import Group, Permission
from users.models.usuario_model import Usuario
from users.repositories.custom_group_repository import CustomGroupRepository


class AuthRepository():
    custom_group_repository = CustomGroupRepository

    def __init__(self):
        from config.shared.di.di import container
        self.custom_group_repository = container.custom_group_repository()

    def find_all_groups(self, order_by="id"):
        queryset = Group.objects.all()
        if order_by:
            queryset = queryset.order_by(order_by)
        return queryset

    def find_all_groups_by_user(self, user_id) -> list[Group]:
        user = Usuario.objects.get(pk=user_id)
        return user.groups.all()

    def find_one_group(self, pk) -> object | None:
        return Group.objects.filter(pk=pk).first()

    def find_all_permissions(self):
        queryset = Permission.objects.all()
        return queryset

    def find_all_permissions_by_group(self, group_id) -> set[Permission]:
        group = Group.objects.get(pk=group_id)
        return group.permissions.all()

    # user_id validated
    def find_all_permissions_by_user(self, user_id) -> list[Permission]:
        user = Usuario.objects.get(pk=user_id)

        # is superuser:
        user_permissions = []
        is_superuser = user.is_superuser
        if is_superuser:
            user_permissions = Permission.objects.all()
        else:
            user_permissions = user.user_permissions.all()
        group_permissions = Permission.objects.filter(
            group__user=user
        ).distinct()
        all_permissions = list(user_permissions) + list(group_permissions)

        return all_permissions

    def find_all_permissions_codename_by_user(self, user_id) -> set[str]:
        user = Usuario.objects.get(pk=user_id)
        return user.get_all_permissions()

    def find_all_modules_by_group(self, group_id) -> set[str] | None:
        group = self.custom_group_repository.find_one(group_id)
        if not group:
            return None
        return group.system_modules
