from datetime import datetime

from crum import get_current_request
from django.contrib.auth.models import Group, Permission
from django.db import models
from django.forms import model_to_dict

from config import settings
from core.security.fields import CustomImageField
from core.user.models import User


class Dashboard(models.Model):
    name = models.CharField(max_length=50, unique=True,
                            help_text='Ingrese un nombre', verbose_name='Nombre')
    icon = models.CharField(
        max_length=500, help_text='Ingrese un icono font awesome', verbose_name='Icono FontAwesome')
    image = CustomImageField(null=True, blank=True, verbose_name='Logo')
    author = models.CharField(max_length=120, null=True, blank=True,
                              help_text='Ingrese un nombre de autor', verbose_name='Autor')
    footer_url = models.CharField(
        max_length=200, null=True, blank=True, help_text='Ingrese una URL', verbose_name='Footer URL')

    def __str__(self):
        return self.name

    def get_image(self):
        if self.image:
            return f'{settings.MEDIA_URL}{self.image}'
        return f'{settings.STATIC_URL}img/src/empty.png'

    class Meta:
        verbose_name = 'Dashboard'
        verbose_name_plural = 'Dashboards'
        default_permissions = ()
        permissions = (
            ('view_dashboard', 'Can view Dashboard'),
        )
        ordering = ['id']


class ModuleType(models.Model):
    name = models.CharField(max_length=150, unique=True,
                            help_text='Ingrese un nombre', verbose_name='Nombre')
    icon = models.CharField(max_length=100, unique=True,
                            help_text='Ingrese un icono font awesome', verbose_name='Icono Font Awesome')

    def __str__(self):
        return self.name

    def get_session_modules(self):
        queryset = []
        request = get_current_request()
        if 'group' in request.session:
            group = request.session['group']
            module_ids = list(group.groupmodule_set.filter(
                module__module_type=self).values_list('module_id', flat=True))
            queryset = Module.objects.filter(
                id__in=module_ids).order_by('name')
        return queryset

    def as_dict(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Tipo de Módulo'
        verbose_name_plural = 'Tipos de Módulos'
        default_permissions = ()
        permissions = (
            ('view_module_type', 'Can view Tipo de Módulo'),
            ('add_module_type', 'Can add Tipo de Módulo'),
            ('change_module_type', 'Can change Tipo de Módulo'),
            ('delete_module_type', 'Can delete Tipo de Módulo'),
        )
        ordering = ['id']


class Module(models.Model):
    name = models.CharField(
        max_length=100, help_text='Ingrese un nombre', verbose_name='Nombre')
    url = models.CharField(max_length=100, unique=True,
                           help_text='Ingrese una URL', verbose_name='URL')
    module_type = models.ForeignKey(
        ModuleType, null=True, blank=True, on_delete=models.PROTECT, verbose_name='Tipo de Módulo')
    description = models.CharField(max_length=200, null=True, blank=True,
                                   help_text='Ingrese una descripción', verbose_name='Descripción')
    icon = models.CharField(max_length=100, null=True, blank=True,
                            help_text='Ingrese un icono font awesome', verbose_name='Icono Font Awesome')
    image = CustomImageField(null=True, blank=True, verbose_name='Imagen')
    permissions = models.ManyToManyField(
        Permission, blank=True, verbose_name='Permisos')

    def __str__(self):
        return f'{self.name} ({self.url})'

    def get_image(self):
        if self.image:
            return f'{settings.MEDIA_URL}{self.image}'
        return f'{settings.STATIC_URL}img/src/empty.png'

    def as_dict(self):
        item = model_to_dict(self)
        item['module_type'] = {
        } if self.module_type is None else self.module_type.as_dict()
        item['image'] = self.get_image()
        item['permissions'] = [model_to_dict(
            i, exclude=['content_type']) for i in self.permissions.all()]
        return item

    class Meta:
        verbose_name = 'Módulo'
        verbose_name_plural = 'Módulos'
        ordering = ['id']


class GroupModule(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)

    def __str__(self):
        return self.module.name

    class Meta:
        verbose_name = 'Grupo Módulo'
        verbose_name_plural = 'Grupo Módulos'
        default_permissions = ()
        ordering = ['id']


class UserAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_joined = models.DateField(default=datetime.now)
    hour = models.TimeField(default=datetime.now)
    remote_addr = models.CharField(max_length=100, null=True, blank=True)
    http_user_agent = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.remote_addr

    def as_dict(self):
        item = model_to_dict(self)
        item['user'] = self.user.as_dict()
        item['date_joined'] = self.date_joined.strftime('%d-%m-%Y')
        item['hour'] = self.hour.strftime('%H:%M %p')
        return item

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        try:
            request = get_current_request()
            self.http_user_agent = str(request.user_agent)
            self.remote_addr = request.META.get('REMOTE_ADDR', None)
        except:
            pass
        super(UserAccess, self).save()

    class Meta:
        verbose_name = 'Acceso de Usuario'
        verbose_name_plural = 'Acceso de Usuarios'
        default_permissions = ()
        permissions = (
            ('view_user_access', 'Can view Acceso de Usuario'),
            ('delete_user_access', 'Can delete Acceso de Usuario'),
        )
        ordering = ['id']


def get_session_module_types(self):
    ids = list(self.groupmodule_set.all().values_list(
        'module__module_type_id', flat=True).distinct())
    return ModuleType.objects.filter(id__in=ids).order_by('name')


def get_session_modules(self):
    ids = list(self.groupmodule_set.filter(
        module__module_type__isnull=True).values_list('module_id', flat=True).distinct())
    return Module.objects.filter(id__in=ids).order_by('name')


Group.add_to_class('get_session_module_types', get_session_module_types)
Group.add_to_class('get_session_modules', get_session_modules)
