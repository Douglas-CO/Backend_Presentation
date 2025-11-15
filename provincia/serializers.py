from rest_framework import serializers
from .models import Provincia
from pais.models import Pais
from pais.serializers import PaisSerializer

class ProvinciaSerializer(serializers.ModelSerializer):
    
    pais_data = serializers.SerializerMethodField()

    class Meta:
        model = Provincia
        fields = [
            "id",
            "nombre",
            "codigo",
            "state",
            "pais",
            "pais_data"
        ]

    def get_pais_data(self, obj):
        return PaisSerializer(obj.pais).data

    def validate_pais(self, value):
        if not Pais.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("El país especificado no existe.")
        return value
