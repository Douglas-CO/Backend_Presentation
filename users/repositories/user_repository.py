from typing import Type, Set
from django.core.exceptions import FieldDoesNotExist
from django.core.exceptions import ValidationError

from config.shared.repositories.base_repository import BaseRepositoryAllMixin

from users.models.usuario_model import Usuario as User


class UserRepository(BaseRepositoryAllMixin):
    model: Type[User]

    def __init__(self, model):
        super().__init__(model)

    def exist_by_username_or_email(self, username, email):
        return self.model.objects.filter(username=username).exists() or self.model.objects.filter(email=email).exists()

    def get_by_username(self, username):
        return self.model.objects.filter(username=username).first()

    def get_user_and_profile_by_username(self, username):
        return self.model.objects.select_related('profile').filter(username=username).first()

    def get_user_permissions(self, user_id) -> Set[str]:  # codename[]
        return self.model.objects.filter(id=user_id).first().get_all_permissions()

    def create(self, data) -> object:
        groups = data.pop('groups', [])
        user = self.model.objects.create(**data)
        if groups:
            user.groups.set(groups)
        return user

    def create_or_update(self, data: dict, unique_field: str) -> object:
        """
        Crea un nuevo registro o actualiza el existente según unique_field.

        - data: dict con pares campo:valor (puede incluir 'groups').
        - unique_field: nombre del campo único por el que buscar (e.g. 'email').
        """
        # 1. Obtener valor de lookup
        if unique_field not in data:
            raise ValidationError(
                f"Debe proporcionar '{unique_field}' en los datos")
        lookup_value = data[unique_field]

        # 2. Separar posibles M2M (por ejemplo 'groups')
        m2m_data = {}
        for field in ('groups',):
            if field in data:
                m2m_data[field] = data.pop(field)

        # 3. Validar solo campos existentes en el modelo
        valid_fields = {f.name for f in self.model._meta.get_fields()}
        invalid = set(data) - valid_fields
        if invalid:
            raise FieldDoesNotExist(
                f"Estos campos no existen en {self.model.__name__}: {invalid}"
            )

        # 4. Preparar defaults sin el campo de lookup
        defaults = {k: v for k, v in data.items() if k != unique_field}

        # 5. Llamar a update_or_create
        obj, created = self.model.objects.update_or_create(
            **{unique_field: lookup_value},
            defaults=defaults
        )

        # 6. Asignar relaciones M2M si las hay
        if 'groups' in m2m_data:
            obj.groups.set(m2m_data['groups'])

        return obj

    def update(self, pk, data) -> object:
        groups = data.pop('groups') if 'groups' in data else None
        user = self.find_one(pk)
        for attr, value in data.items():
            setattr(user, attr, value)
        user.save()
        if groups is None:
            return user
        if len(groups) == 0:
            user.groups.clear()
            return user
        user.groups.set(groups)
        return user

    def find_one_by_attrs(self, params: dict):
        # {attr: value, attr2: value2, ...}
        return self.model.objects.filter(**params).first()
