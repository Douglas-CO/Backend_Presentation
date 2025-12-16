from typing import Type
from django.contrib.auth.hashers import make_password  # hashear password
from django.db.utils import IntegrityError
from django.db import transaction
from config.shared.utils.common_utils import clear_cache_key_get_all

from config.shared.services.base_service import BaseServiceAllMixin
from config.shared.exceptions.bad_request_exception import BadRequestException
from config.shared.exceptions.resource_not_found_exception import ResourceNotFoundException
from config.shared.exceptions.invalid_fields_exception import InvalidFieldsException

from users.repositories.user_repository import UserRepository
from users.filters.user_filters import UserFilter
from users.serializers.user_serializers import UserCreateSerializer, UserResponseSerializer, UserUpdateSerializer
from users.shared.utils.utils import validate_password
from django.core.exceptions import ValidationError
from config.shared.exceptions.custom_generic_exception import CustomGenericException


class UserService(BaseServiceAllMixin):
    repository: Type[UserRepository]

    filter = UserFilter

    serializer = UserCreateSerializer
    serializer2 = UserResponseSerializer
    upd_serializer = UserUpdateSerializer

    def __init__(self, repository, employee_service):
        super().__init__(repository, filter=self.filter,
                         serializer=self.serializer, serializer2=self.serializer2)
        self.employee_service = employee_service

    def create_user(self, data):
        try:
            serializer_data = self.serializer(data=data)
            if not serializer_data.is_valid():
                raise InvalidFieldsException(
                    message="Bad Request", fields=serializer_data.errors.items()
                )

            if self.repository.exist_by_username_or_email(data['username'], data['email']):
                raise BadRequestException(
                    'El usuario o email ya ha sido registrado'
                )

            # work with transaction to automatically rollback if something goes wrong
            password = data.get('password', None)
            validate_password(password)
            with transaction.atomic():
                saved_user = self.repository.create({
                    'username': data['username'],
                    'email': data['email'],
                    'password': make_password(data['password']),
                    'razon_social': data['razon_social'],
                    'groups': data['groups'] if 'groups' in data else [],
                    # profile
                    'tipo_identificacion': data['tipo_identificacion'],
                    'identificacion': data['identificacion'],
                    # company logic
                    'centro_costo_id': data['centro_costo'] if 'centro_costo' in data else None,
                    'area_id': data['area'] if 'area' in data else None,
                    'departamento_id': data['departamento'] if 'departamento' in data else None,
                    'canal_venta_id': data['canal_venta'] if 'canal_venta' in data else None,
                    'role': data['role'] if 'role' in data else 'AGENTE',
                })

                # create employee
                if 'create_employee' in data and data['create_employee']:
                    self.employee_service.create({
                        **data,
                        'user': saved_user.id,
                    })

            # clear employee cache
            clear_cache_key_get_all('Empleado')

            return {
                "user": self.serializer2(saved_user).data,
            }
        except Exception as e:
            if isinstance(e, IntegrityError):
                print('===============================',
                      e, '===============================')
                raise ResourceNotFoundException(
                    message="Grupo no encontrado"
                )
            raise e

    # @Override
    def find_all(self, filter_params=None, page_number=..., page_size=...):
        queryset = self.find_all_mx(self.filter, filter_params)
        paginated_data = self.paginate_queryset(
            queryset, page_number, page_size)
        serialized_data_list = self.serialize(
            paginated_data["page_obj"], many=True)

        # serialize employee if exists ------------
        transformed_data = []
        try:
            for item in list(serialized_data_list or []):
                # service already serialized employee
                employee = self.employee_service.find_one_by_attr(
                    'user_id', item['id'])
                transformed_data.append({
                    'user': item,
                    'employee': employee,
                })
        except Exception as e:
            if isinstance(e, ResourceNotFoundException):
                transformed_data = [
                    {'user': item, 'employee': None}
                    for item in list(serialized_data_list or [])
                ]
            else:
                raise e

        return {
            "meta": {
                "next": paginated_data["next_page"],
                "previous": paginated_data["previous_page"],
                "count": paginated_data["count"],
                "total_pages": paginated_data["total_pages"],
            },
            "data": transformed_data,
        }

    def find_one(self, pk) -> dict:
        user_instance = self.repository.find_one(pk)
        if not user_instance:
            raise ResourceNotFoundException(
                message="Usuario no encontrado"
            )
        return {
            "user": self.serializer2(user_instance).data,
        }

    def find_one_by_uuid(self, uuid) -> dict:
        instance = self.find_one_by_uuid_mx(uuid)

        # serialize employee if exists
        try:
            # service already serialized employee
            employee = self.employee_service.find_one_by_attr(
                'user_id', instance.id if instance else None)
        except Exception as e:
            if isinstance(e, ResourceNotFoundException):
                employee = None
            else:
                raise e

        return {
            "user": self.serializer2(instance).data,
            "employee": employee,
        }

    def update(self, pk, data) -> dict:
        try:
            instance = self.get_by_id(pk)
            if not instance:
                raise InvalidFieldsException(
                    message="Invalid fields"
                )

            serializer_data = self.upd_serializer(
                instance, data=data, partial=True, context={'pk': pk})
            if not serializer_data.is_valid():
                raise InvalidFieldsException(
                    message="Invalid fields",
                    fields=serializer_data.errors.items()
                )

            user_data_to_upd = {
                key: value for key, value in serializer_data.validated_data.items() if key not in ['id', 'uuid', 'created_at', 'updated_at', 'numero_referencia', 'codigo']
            }

            with transaction.atomic():
                password = data['password'] if 'password' in data else None
                is_valid_password = validate_password(
                    password) if password else False

                centro_costo_id = data.pop('centro_costo', None)
                area_id = data.pop('area', None)
                departamento_id = data.pop(
                    'departamento', None)
                canal_venta_id = data.pop(
                    'canal_venta', None)
                role = data.pop('role', None)

                updated_user = self.repository.update(
                    pk, data={
                        **user_data_to_upd,
                        'password': make_password(password) if is_valid_password else instance.password,
                        'centro_costo_id': centro_costo_id,
                        'area_id': area_id,
                        'departamento_id': departamento_id,
                        'canal_venta_id': canal_venta_id,
                        'role': role,
                        'groups': data['groups'] if 'groups' in data else instance.groups,
                    }
                )

            # clear employee cache
            clear_cache_key_get_all('Empleado')
            clear_cache_key_get_all('Usuario')
            return {
                "user": self.serializer2(updated_user).data,
            }
        except Exception as e:
            if isinstance(e, IntegrityError):
                print(e)
                raise ResourceNotFoundException(
                    message="Grupo no encontrado"
                )
            raise e

    def get_by_id(self, pk):
        return self.repository.find_one(pk)

    def unblock_user(self, pk):
        user_instance = self.find_one_active_instance(pk)

        user_instance.intentos_fallidos = 0
        user_instance.save()

        clear_cache_key_get_all('Empleado')
        clear_cache_key_get_all('Usuario')
        return {
            "user": self.serializer2(user_instance).data,
        }

    def change_password(self, pk, data, user_i=None):
        user = self.find_one_active_instance(pk)
        if not user:
            raise CustomGenericException(
                message="Usuario no encontrado",
                status=404
            )

        new_pwd = data.get('new_password')
        confirm_pwd = data.get('confirm_new_password')

        if not new_pwd:
            raise CustomGenericException(
                message="Invalid fields",
                data={'new_password': ['Este campo es obligatorio']},
                status=400
            )
        if not confirm_pwd:
            raise CustomGenericException(
                message="Invalid fields",
                data={'confirm_new_password': ['Este campo es obligatorio']},
                status=400
            )
        if new_pwd != confirm_pwd:
            raise CustomGenericException(
                message="Invalid fields",
                data={'new_password': ['Las contraseñas no coinciden']},
                status=400
            )

        try:
            validate_password(new_pwd)
        except ValidationError as e:
            raise CustomGenericException(
                message="Invalid fields",
                data={'new_password': e.messages},
                status=400
            )

        user.password = make_password(new_pwd)
        user.save()
        clear_cache_key_get_all('Empleado')
        clear_cache_key_get_all('Usuario')
        return {"user": self.serializer2(user).data}

    def desactivate_user(self, pk, user_i=None):
        user = self.find_one_active_instance(pk)
        if not user:
            raise CustomGenericException(
                message="Usuario no encontrado",
                status=404
            )

        user.state = False
        user.save()
        # clear_cache_key_get_all('Empleado')
        # clear_cache_key_get_all('Usuario')
        return {"user": self.serializer2(user).data}
