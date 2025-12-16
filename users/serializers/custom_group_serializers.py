from rest_framework import serializers

from config.shared.serializers.serializers import (
    FiltersBaseSerializer,
    QueryDocWrapperSerializer,
    QueryListDocWrapperSerializer
)
from users.models.custom_group_model import CustomGroup


# ### CustomGroup Serializer - Model ===============
# override permissions as int[] to string[] en validacion del serializer model
class CustomGroupSerializer(serializers.ModelSerializer):
    permissions = serializers.ListField(
        child=serializers.CharField(max_length=255), required=False)

    class Meta:
        model = CustomGroup
        fields = '__all__'

    # custom validation
    def validate_permissions(self, value):
        from django.contrib.auth.models import Permission

        if not value:
            return value
        if not isinstance(value, list):
            raise serializers.ValidationError(
                'El campo permissions debe ser una lista de strings')

        # check if permissions are valid
        valid_permissions = set(
            Permission.objects.values_list('codename', flat=True))
        invalid_permissions = [
            perm for perm in value if perm not in valid_permissions]

        if invalid_permissions:
            raise serializers.ValidationError(
                f'Permisos inválidos: {", ".join(invalid_permissions)}'
            )
        return value


# ## Response: Get All & Get By ID
class CustomGroupResponseSerializer(FiltersBaseSerializer):
    class Meta:
        model = CustomGroup
        fields = '__all__'


class CustomGroupLimitResponseSerializer(FiltersBaseSerializer):
    class Meta:
        model = CustomGroup
        fields = ['uuid', 'id', 'codigo', 'description', 'name']


# ### Filter Serializer - Get All ===============
class CustomGroupFilterSerializer(FiltersBaseSerializer):
    class Meta:
        model = CustomGroup
        fields = '__all__'


# ### Swagger ===============
# ## Response Body: Post & Put & Patch
class CustomGroupOptDocSerializer(FiltersBaseSerializer):
    class Meta:
        model = CustomGroup
        fields = '__all__'


class CustomGroupOptDocWrapperSerializer(QueryDocWrapperSerializer):
    data = CustomGroupResponseSerializer(required=False)


# ## Get All Response
class CustomGroupQueryDocWrapperSerializer(QueryListDocWrapperSerializer):
    data = CustomGroupResponseSerializer(many=True, required=False)
