from config.shared.filters.filters import BaseFilter
from log.models.role_model import Role


class RoleFilter(BaseFilter):
    class Meta:
        model = Role
        fields = '__all__'
