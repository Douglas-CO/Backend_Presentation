from rest_framework import serializers


from config.shared.serializers.serializers import (
    FiltersBaseSerializer,
    QueryListDocWrapperSerializer,
    QueryDocWrapperSerializer,
    OptionalFieldsModelSerializer,
)
from users.models.usuario_model import Usuario as User
from config.shared.constants.choices import USER_ROLES
from users.shared.utils.utils import validate_password


# ### User Serializer - Model ===============
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class BaseUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, help_text='Username')
    # Hacerlo opcional solo en la base si es común
    password = serializers.CharField(
        write_only=True, help_text='Password', required=True, validators=[validate_password])
    email = serializers.EmailField(help_text='Email')
    razon_social = serializers.CharField(
        max_length=200, help_text='Razón Social')
    # name = serializers.CharField(max_length=100, help_text='Nombre')
    # last_name = serializers.CharField(max_length=100, help_text='Apellido')
    tipo_identificacion = serializers.ChoiceField(
        choices=['CEDULA', 'RUC', 'PASAPORTE'], help_text='Tipo de identificación')
    identificacion = serializers.CharField(
        max_length=20, help_text='Identificación')
    groups = serializers.ListField(
        child=serializers.IntegerField(), help_text='Grupos', required=False)
    # user_permissions = serializers.ListField(
    #     child=serializers.IntegerField(), help_text='Permisos', required=False)
    # empresa = serializers.IntegerField(help_text='Empresa')
    # area = serializers.IntegerField(help_text='Área')
    # departamento = serializers.IntegerField(help_text='Departamento')
    # canal_venta = serializers.IntegerField(
    #     help_text='Canal de Venta', required=False, allow_null=True)
    # role = serializers.ChoiceField(
    #     choices=USER_ROLES, help_text='Rol')


class UserCreateSerializer(BaseUserSerializer):
    def __init__(self, *args, **kwargs):
        super(UserCreateSerializer, self).__init__(*args, **kwargs)
        # ## DI
        # to avoid circular imports
        from config.shared.di.di import container
        self.user_repository = container.user_repository()

    # creation validation
    def validate_username(self, value):
        sent_id = self.context.get('pk', None)  # controlled by view
        user = self.user_repository.find_one_by_attr("username", value)
        if user and (user.id != sent_id):
            raise serializers.ValidationError("Este username ya está en uso.")
        return value

    def validate_email(self, value):
        sent_id = self.context.get('pk', None)
        user = self.user_repository.find_one_by_attr("email", value)
        if user and (user.id != sent_id):
            raise serializers.ValidationError("Este email ya está en uso.")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True, help_text='New Password', required=True, validators=[validate_password])
    confirm_new_password = serializers.CharField(
        write_only=True, help_text='Confirm New Password', required=True, validators=[validate_password])

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return attrs


# just for documentation


class UserUpdateSerializer(BaseUserSerializer):
    def __init__(self, *args, **kwargs):
        super(UserUpdateSerializer, self).__init__(*args, **kwargs)
        # make all fields optional
        for field in self.fields.values():
            field.required = False


# ## Response: Get All & Get By ID
class UserResponseSerializer(FiltersBaseSerializer):
    permissions = serializers.ListField(
        child=serializers.CharField(), required=False)

    # property ----------
    is_valid_salesman = serializers.BooleanField()

    class Meta:
        model = User
        exclude = ['password', 'is_staff',
                   'last_login', 'created_at', 'modified_at', 'user_permissions']


class UserLoginResponseSerializer(FiltersBaseSerializer):
    permissions = serializers.ListField(
        child=serializers.CharField(), required=False)

    class Meta:
        model = User
        exclude = ['password', 'is_staff', 'is_superuser',
                   'last_login', 'created_at', 'modified_at', 'user_permissions']


class UserLimitResponseSerializer(FiltersBaseSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'razon_social',
                  'uuid', 'role', 'id', 'canal_venta_data']


class UserLimitRespSerializer(OptionalFieldsModelSerializer):
    class Meta:
        model = User
        fields = [
            'razon_social', 'role', 'id', 'uuid',
        ]


# ### Filter Serializer - Get All -------
class UserFilterSerializer(FiltersBaseSerializer):
    class Meta:
        model = User
        fields = "__all__"


# ### Swagger ===============
# ## Response Body: Post & Put & Patch
class UserOptDocSerializer(FiltersBaseSerializer):
    class Meta:
        model = User
        fields = "__all__"


class UserOptDocWrapperSerializer(QueryDocWrapperSerializer):
    data = UserOptDocSerializer(required=False)


# ## Get all response
class UserQueryDocWrapperSerializer(QueryListDocWrapperSerializer):
    data = UserResponseSerializer(many=True, required=False)
