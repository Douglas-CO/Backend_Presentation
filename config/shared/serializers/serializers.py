from typing import List, Optional
from rest_framework import serializers


# ### Filters ========================
class FiltersBaseSerializer(serializers.ModelSerializer):
    # model editable=False doesn't render in filter serializer
    uuid = serializers.UUIDField(required=False)
    # global filters for docs - controlled by base service
    order_by = serializers.CharField(required=False)
    order_by_asc = serializers.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(FiltersBaseSerializer, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False


# ### Swagger ========================
class OptionalFieldsModelSerializer(serializers.ModelSerializer):
    def get_fields(self, *args, **kwargs):
        fields = super(OptionalFieldsModelSerializer,
                       self).get_fields(*args, **kwargs)
        for field in fields.values():
            field.required = False
        return fields


class OptionalFieldsSerializer(serializers.Serializer):
    def get_fields(self, *args, **kwargs):
        fields = super(OptionalFieldsSerializer,
                       self).get_fields(*args, **kwargs)
        for field in fields.values():
            field.required = False
        return fields


# ## Get all
class GenericBaseSerializer(serializers.Serializer):
    status = serializers.IntegerField(required=False)
    message = serializers.CharField(required=False)
    data = serializers.CharField(required=False, allow_null=True)


class MetaSerializer(serializers.Serializer):
    next = serializers.IntegerField(required=False, allow_null=True)
    previous = serializers.IntegerField(required=False, allow_null=True)
    count = serializers.IntegerField(required=False, allow_null=True)
    total_pages = serializers.IntegerField(required=False, allow_null=True)


class QueryListDocWrapperSerializer(GenericBaseSerializer):
    meta = MetaSerializer(required=False, allow_null=True)
    data = serializers.ListField(required=False, allow_null=True)


class QueryDocWrapperSerializer(GenericBaseSerializer):
    data = serializers.DictField(required=False, allow_null=True)
    # invalid_fields = serializers.ListField(required=False, allow_null=True) # nullable - serializer validation


# ### Errors ========================
class BadRequestSerializer(GenericBaseSerializer):
    invalid_fields = serializers.ListField(
        child=serializers.CharField(), required=False
    )


class NotFoundSerializer(serializers.Serializer):
    status = serializers.IntegerField(required=False)
    message = serializers.CharField(required=False)


# ---------------------------------
class ErrorResponseDTO:
    def __init__(
        self,
        status: int,
        message: str,
        invalid_fields: Optional[List[str]] = None,
        data: Optional[dict] = None,
    ):
        self.status = status
        self.message = message
        self.invalid_fields = invalid_fields
        self.data = data


class NotFoundErrorResponseDTO:
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message


class UnauthorizedErrorResponseDTO:
    def __init__(self, status: int, message: str, data: Optional[dict] = None):
        self.status = status
        self.message = message
        self.data = data
