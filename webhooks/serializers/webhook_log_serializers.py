from rest_framework import serializers

from config.shared.serializers.serializers import (
    FiltersBaseSerializer,
    QueryDocWrapperSerializer,
    QueryListDocWrapperSerializer
)
from webhooks.models.webhook_log_model import WebhookLog


# ### WebhookLog Serializer - Model ===============
class WebhookLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookLog
        fields = '__all__'


class WebhookSuccessPaymentSerializer(serializers.Serializer):
    contrapartida = serializers.CharField()

    estadoPago = serializers.CharField()
    mensaje = serializers.CharField()
    idTransaccion = serializers.CharField()
    numeroAutorizacion = serializers.CharField()
    valorPagado = serializers.CharField()
    fechaPago = serializers.CharField()
    fechaContable = serializers.CharField()
    fecha_pago_dt = serializers.DateTimeField(required=False, allow_null=True)

    rubros = serializers.JSONField()
    # facturas = serializers.JSONField()

    # hashedToCompare = serializers.CharField()
    switchSignature = serializers.CharField()

    ifi = serializers.CharField(required=False, allow_blank=True)

    def validate_rubros(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError('rubros debe ser una lista')
        return value

    def validate_facturas(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError('facturas debe ser una lista')
        return value


# ## Response: Get All & Get By ID ===============
class WebhookLogResponseSerializer(FiltersBaseSerializer):
    class Meta:
        model = WebhookLog
        fields = '__all__'


class WebhookLogLimitResponseSerializer(FiltersBaseSerializer):
    class Meta:
        model = WebhookLog
        fields = ['name', 'uuid']


# ### Filter Serializer - Get All ===============
class WebhookLogFilterSerializer(FiltersBaseSerializer):
    class Meta:
        model = WebhookLog
        fields = '__all__'


# ### Swagger ===============
# ## Response Body: Post & Put & Patch
class WebhookLogOptDocWrapperSerializer(QueryDocWrapperSerializer):
    data = WebhookLogResponseSerializer(required=False)


# ## Get All Response
class WebhookLogQueryDocWrapperSerializer(QueryListDocWrapperSerializer):
    data = WebhookLogResponseSerializer(many=True, required=False)
