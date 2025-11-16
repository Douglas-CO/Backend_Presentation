from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Usuario, Grupo

class GrupoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grupo
        fields = ["id", "name", "system_modules", "permissions"] 


class UsuarioSerializer(serializers.ModelSerializer):
    grupo_data = GrupoSerializer(source="grupo", read_only=True)

    class Meta:
        model = Usuario
        fields = ["id", "username", "password", "email", "grupo", "grupo_data"]
        read_only_fields = ["id", "grupo_data"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Usuario o contraseña incorrectos")

        return {"user": user} 

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    grupo = serializers.PrimaryKeyRelatedField(
        queryset=Grupo.objects.all(), required=True)

    class Meta:
        model = Usuario
        fields = ["username", "email", "password", "grupo"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()
        return user
