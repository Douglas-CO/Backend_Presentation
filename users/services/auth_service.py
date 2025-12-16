from rest_framework.authtoken.models import Token
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage, PageNotAnInteger

from config.shared.services.common.multitenant_service import MultitenantService

from config.shared.exceptions.bad_request_exception import BadRequestException
from config.shared.exceptions.resource_not_found_exception import ResourceNotFoundException
from config.shared.exceptions.conflicts_exception import ConflictsException
from config.shared.exceptions.locked_request_exception import LockedRequestException
from config.shared.exceptions.unauthorized_exception import UnauthorizedException

from users.repositories.user_repository import UserRepository
from users.repositories.auth_repository import AuthRepository
from users.serializers.user_serializers import UserResponseSerializer
from users.serializers.auth_serializers import PermissionSerializer

from config.shared.constants.constants import (
    PAGINATION_DEFAULT_PAGE_NUMBER,
    PAGINATION_DEFAULT_PAGE_SIZE,
)
from users.shared.constants.system_modules import system_modules_sidenav

from config.shared.services.common.multitenant_static_helper import MultitenantStaticHelper

from webhooks.services.auditoria_log_service import ESLogService

from types import SimpleNamespace


import environ
import os
from config import settings
env = environ.Env()
environ.Env.read_env(os.path.join(settings.BASE_DIR, '.env'))


class AuthService():
    repository: UserRepository
    auth_repository: AuthRepository
    multitenant_service: MultitenantService

    filter = None

    serializer = None
    serializer2 = None
    user_serializer = UserResponseSerializer
    permission_serializer = PermissionSerializer

    def __init__(self, repository, auth_repository, multitenant_service, flota_repository):
        self.repository = repository  # DI
        self.auth_repository = auth_repository  # DI
        self.multitenant_service = multitenant_service  # DI
        self.flota_repository = flota_repository  # DI

    def login(self, data, ip: str, os: str, request=None):
        user = self.repository.find_one_by_attr(
            attr='username', value=data['username'])
        if not user:
            raise BadRequestException('Creedenciales incorrectas')

        failed_attempts = user.intentos_fallidos
        max_attempts = env.int('MAX_LOGIN_ATTEMPTS', default=3)
        if failed_attempts >= max_attempts:
            raise LockedRequestException('Usuario bloqueado')

        if not user.state:
            raise UnauthorizedException(
                message='Usuario desactivado.',
            )

        if not user.check_password(data['password']):
            self.repository.update(user.id, {
                'intentos_fallidos': failed_attempts + 1
            })
            raise UnauthorizedException(
                message='Creedenciales incorrectas',
                data={
                    'failed_attempts': failed_attempts + 1
                }
            )

        # ### CORE LOGIC --------------------------------------------
        force_login = data.get('force_login', False)
        token, created = Token.objects.get_or_create(user=user)

        if not created:
            # Check if the user is trying to force login
            if force_login:
                token.delete()  # Delete the existing token
                token = Token.objects.create(user=user)  # Create a new token
            else:
                raise ConflictsException(message=f"Ya existe una sesión activa para este usuario en la dirección IP {user.ip_login} y el OS {user.os_login}.", data={
                    "ip": user.ip_login,
                    "os": user.os_login,
                })

        self.repository.update(user.id, {
            'ip_login': ip,
            'os_login': os,
            'intentos_fallidos': 0
        })

        user_permissions = self.auth_repository.find_all_permissions_codename_by_user(
            user.id)
        user.permissions = sorted(user_permissions)

        # Get system modules
        system_modules = []
        if user.is_superuser or user.is_staff:
            system_modules = system_modules_sidenav
        else:
            groups = self.auth_repository.find_all_groups_by_user(user.id)
            for group in groups:
                group_modules = self.auth_repository.find_all_modules_by_group(
                    group.id)
                system_modules += group_modules

        self._log_login_success_no_2fa(
            user=user, ip=ip, os=os, request=request)
        payload = self._build_login_payload(user)
        return {
            "token": token.key,
            **payload,
            # "user": self.user_serializer(user).data,
            # "system_modules":  list(set(system_modules)),
            # "company_data": company_serializer.data,
            # "flota_data": fllet_serializer if fllet_serializer else None
        }

    def get_user_permissions(self, user_id, page_number=PAGINATION_DEFAULT_PAGE_NUMBER, page_size=PAGINATION_DEFAULT_PAGE_SIZE):
        user = self.repository.find_one(user_id)
        if not user:
            raise ResourceNotFoundException(
                message=f"User with id '{user_id}' not found"
            )
        queryset = self.auth_repository.find_all_permissions_by_user(
            user_id)
        # pagination
        return self._paginate_permissions_qs(queryset, page_number, page_size)

    def get_group_permissions(self, group_id, page_number=PAGINATION_DEFAULT_PAGE_NUMBER, page_size=PAGINATION_DEFAULT_PAGE_SIZE):
        group = self.auth_repository.find_one_group(group_id)
        if not group:
            raise ResourceNotFoundException(
                message=f"Group with id '{group_id}' not found"
            )
        queryset = self.auth_repository.find_all_permissions_by_group(
            group_id)
        # pagination
        return self._paginate_permissions_qs(queryset, page_number, page_size)

    def find_all_permissions(self, page_number=PAGINATION_DEFAULT_PAGE_NUMBER, page_size=PAGINATION_DEFAULT_PAGE_SIZE):
        queryset = self.auth_repository.find_all_permissions()
        # pagination
        return self._paginate_permissions_qs(queryset, page_number, page_size)

    def _paginate_permissions_qs(self, queryset, page_number, page_size):
        paginator = Paginator(queryset, page_size)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = []

        if isinstance(page_obj, list):
            next_page = previous_page = None
            count = total_pages = 0
        else:
            next_page = page_obj.next_page_number() if page_obj.has_next() else None
            previous_page = (
                page_obj.previous_page_number() if page_obj.has_previous() else None
            )
            count = paginator.count
            total_pages = paginator.num_pages

        # serializer
        serializer = self.permission_serializer(page_obj, many=True)
        return {
            "meta": {
                "next": next_page,
                "previous": previous_page,
                "count": count,
                "total_pages": total_pages,
            },
            "data": serializer.data,
        }

    def _build_login_payload(self, user):
        # permissions
        user_permissions = self.auth_repository.find_all_permissions_codename_by_user(
            user.id)
        user.permissions = sorted(user_permissions)

        # system modules
        system_modules = []
        if user.is_superuser or user.is_staff:
            system_modules = system_modules_sidenav
        else:
            groups = self.auth_repository.find_all_groups_by_user(user.id)
            for group in groups:
                group_modules = self.auth_repository.find_all_modules_by_group(
                    group.id)
                system_modules += group_modules

        # company
        company = self.multitenant_service.get_current_company()
        company_serializer = self.company_serializer(company)

        # flota
        fleet_i = self.flota_repository.find_one_by_attrs({'user_id': user.id})

        # payload igual al login normal
        return {
            # el front luego separa permissions
            "user": self.user_serializer(user).data,
            "system_modules": list(set(system_modules)),
            "company_data": company_serializer.data,
            # opcional si quieres devolverlo explícito
            "permissions": user.permissions,
        }

    def _log_login_success_no_2fa(self, *, user, ip: str, os: str, request=None):
        """
        Registra en ES que el usuario inició sesión SIN 2FA.
        Inyecta temporalmente request.user = user para que build_audit_payload
        pueble user.id/username/ip/ua/schema correctamente.
        """
        try:
            # --- construir/normalizar request ---
            if request is None:
                # request “lite”
                class _ReqLite:
                    def __init__(self, user, ip, ua):
                        self.user = user
                        self.method = "POST"
                        self._path = "/auth/login"
                        self.resolver_match = None
                        self.META = {
                            "REMOTE_ADDR": ip,
                            "HTTP_X_FORWARDED_FOR": ip,
                            "HTTP_USER_AGENT": ua or "",
                        }
                        schema = MultitenantStaticHelper.get_current_schema()
                        self.tenant = SimpleNamespace(schema_name=schema)

                    def get_full_path(self): return self._path
                    @property
                    def path(self): return self._path

                req = _ReqLite(user, ip, os)
            else:
                # asegúrate de tener lo mínimo
                req = request
                if not hasattr(req, "META") or req.META is None:
                    req.META = {}
                req.META.setdefault("HTTP_X_FORWARDED_FOR", ip or "")
                req.META.setdefault("REMOTE_ADDR", ip or "")
                req.META.setdefault("HTTP_USER_AGENT", os or "")
                if not hasattr(req, "method") or req.method is None:
                    req.method = "POST"
                if not hasattr(req, "get_full_path"):
                    req.get_full_path = lambda: "/auth/login"
                if not hasattr(req, "path"):
                    req.path = "/auth/login"
                if not hasattr(req, "tenant"):
                    schema = MultitenantStaticHelper.get_current_schema()
                    req.tenant = SimpleNamespace(schema_name=schema)

            # --- payload (lo demás lo completa build_audit_payload) ---
            no_user_log_es = ['consulta_externa2']
            payload = {
                "action": "AUTH_LOGIN",
                "resource": "auth.login",
                "resource_id": getattr(user, "id", None),
                "description": f"LOGIN EXITOSO SIN 2FA PARA {getattr(user, 'username', 'anonymous')}",
                "method": req.method,
                "route": getattr(getattr(req, "resolver_match", None), "route", None),
                "full_path": req.get_full_path() if hasattr(req, "get_full_path") else req.path,
                "extra": {
                    "used_2fa": False,
                    "ip": ip,
                    "os": os,
                },
                "http_status": 200,
                "is_sensitive": False,
            }

            # --- swap temporal del user para que build_audit_payload tome username/id ---
            original_user = getattr(req, "user", None)
            username = getattr(user, "username", None)
            try:
                if username not in no_user_log_es:
                    req.user = user
                    ESLogService(timeout=3).write_sync_from_request(
                        req, payload)
            finally:
                req.user = original_user

        except Exception as e:
            # nunca bloquear el login por el logging
            print(f"Error logging login success without 2FA: {e}")
            pass
