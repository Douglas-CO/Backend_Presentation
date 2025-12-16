from django.contrib.auth.models import Permission
from rest_framework import serializers

from config.shared.serializers.serializers import QueryDocWrapperSerializer
from users.serializers.user_serializers import UserLoginResponseSerializer


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(max_length=100, required=True)
    force_login = serializers.BooleanField(default=False, required=False)


class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=100, required=False)
    user = UserLoginResponseSerializer(required=False)
    system_modules = serializers.ListField(
        child=serializers.CharField(), required=False)


class LoginResponseDocWrapperSerializer(QueryDocWrapperSerializer):
    data = LoginResponseSerializer(required=False)


# ### Authorization ========================
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class PermissionListQueryDocWrapperSerializer(serializers.Serializer):
    data = serializers.ListField(child=serializers.CharField(), required=False)
