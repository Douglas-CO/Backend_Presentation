from rest_framework import serializers


class AuditLogQuerySerializer(serializers.Serializer):
    q = serializers.CharField(required=False, allow_blank=True)
    action = serializers.CharField(required=False)
    resource = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    schema_name = serializers.CharField(required=False)
    user_id = serializers.IntegerField(required=False)
    resource_id = serializers.CharField(required=False)
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    limit = serializers.IntegerField(
        required=False, min_value=1, max_value=1000, default=50)
    offset = serializers.IntegerField(required=False, min_value=0, default=0)
    sort = serializers.ChoiceField(required=False, choices=[
                                   "-timestamp", "timestamp"], default="-timestamp")


class AuditLogSerializer(serializers.Serializer):
    uuid = serializers.CharField()
    timestamp = serializers.DateTimeField()
    action = serializers.CharField()
    resource = serializers.CharField(allow_null=True)
    resource_id = serializers.CharField(allow_null=True)
    username = serializers.CharField(allow_null=True)
    schema_name = serializers.CharField(allow_null=True)
    description = serializers.CharField(allow_null=True)
    ip = serializers.CharField(allow_null=True)
    user_id = serializers.IntegerField(allow_null=True)
    user_uuid = serializers.CharField(allow_null=True)
    user_agent = serializers.CharField(allow_null=True)
    customer_full_name = serializers.CharField(allow_null=True)
    service_line_uuid = serializers.CharField(allow_null=True)
    extra = serializers.JSONField()
    method = serializers.CharField(allow_null=True)
    route = serializers.CharField(allow_null=True)
    full_path = serializers.CharField(allow_null=True)
    is_sensitive = serializers.BooleanField(default=False)

    class Meta:
        ref_name = "CarteraAuditLog"


class PaginatedAuditLogResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    results = AuditLogSerializer(many=True)


# ------------------
class AuditLogCreateSerializer(serializers.Serializer):
    # Requeridos (mínimos)
    action = serializers.CharField(max_length=64)
    resource = serializers.CharField(max_length=128)

    # Opcionales
    description = serializers.CharField(allow_blank=True, required=False)
    resource_id = serializers.CharField(allow_blank=True, required=False)
    customer_full_name = serializers.CharField(
        allow_blank=True, required=False)
    service_line_uuid = serializers.UUIDField(required=False, allow_null=True)
    extra = serializers.DictField(required=False)
    http_status = serializers.IntegerField(
        required=False, min_value=100, max_value=599)
    is_sensitive = serializers.BooleanField(required=False, default=False)

    def validate_action(self, value: str) -> str:
        v = (value or "").strip()
        if not v:
            raise serializers.ValidationError("action es requerido")
        return v

    def validate(self, attrs):
        # Normalizaciones leves
        if "service_line_uuid" in attrs and attrs["service_line_uuid"] is None:
            attrs.pop("service_line_uuid")
        return attrs
