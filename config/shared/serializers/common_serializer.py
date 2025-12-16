from core.multicpy.models import Company
from rest_framework import serializers

from config.shared.serializers.serializers import OptionalFieldsModelSerializer
from config.shared.exceptions.invalid_fields_exception import InvalidFieldsException


class CompanyLimitResponseSerializer(OptionalFieldsModelSerializer):
    class Meta:
        model = Company
        fields = [
            'uuid', 'id', 'company_name', 'commercial_name', 'logo_1_url', 'logo_2_url', 'schema_name', 'email', 'main_address', 'establishment_address', 'mobile', 'phone'
        ]
# http://localhost:5173/clientes/fibra-optica/5652f97b-daeb-474e-b75b-b8a54a5a5b11


class RegisterUserClientOfiVirtualSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=255)
    full_name = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255)


# ========================================
class CommonSerializerStaticHelper:

    @staticmethod
    def validate_and_serialize_by_serializer(data, serializer):
        serialized = serializer(data=data)
        if serialized.is_valid():
            return serialized.validated_data
        raise InvalidFieldsException(
            message="Bad Request", fields=serialized.errors.items()
        )

    @staticmethod
    def serialize_by_serializer(instance, serializer, many=False):
        serialized = serializer(instance, many=many)
        return serialized.data
