from rest_framework import serializers

from log.models.role_model import Role
from config.shared.serializers.serializers import (
    FiltersBaseSerializer,
    QueryDocWrapperSerializer,
    QueryListDocWrapperSerializer,
)


# ### Role Serializer - Model ===============
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


# ## Response: Get All & Get By ID
class RoleResponseSerializer(FiltersBaseSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class RoleLimitResponseSerializer(FiltersBaseSerializer):
    class Meta:
        model = Role
        fields = ['name', 'uuid', 'id', 'code']


# ### Filter Serializer - Get All ===============
class RoleFilterSerializer(FiltersBaseSerializer):
    class Meta:
        model = Role
        fields = '__all__'


# ### Swagger ===============
# ## Response Body: Post & Put & Patch
class RoleOptDocWrapperSerializer(QueryDocWrapperSerializer):
    data = RoleResponseSerializer(required=False)


# ## Get All Response
class RoleQueryDocWrapperSerializer(QueryListDocWrapperSerializer):
    data = RoleResponseSerializer(many=True, required=False)
