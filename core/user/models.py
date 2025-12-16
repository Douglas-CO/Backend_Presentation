import uuid

from crum import get_current_request
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager
from django.db import models
from django.forms.models import model_to_dict
from django.utils import timezone

from config import settings
from core.security.fields import CustomImageField


class User(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True,
                                help_text='Ingrese un username', verbose_name='Username')
    image = CustomImageField(upload_to='user/%Y/%m/%d',
                             null=True, blank=True, verbose_name='Imagen')
    email = models.EmailField(
        null=True, blank=True, help_text='Ingrese un email', verbose_name='Correo electrónico')
    is_active = models.BooleanField(default=True, verbose_name='Estado')
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    is_change_password = models.BooleanField(default=False)
    email_reset_token = models.TextField(null=True, blank=True)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def as_dict(self):
        item = model_to_dict(self, exclude=[
                             'last_login', 'email_reset_token', 'password', 'user_permissions'])
        item['image'] = self.get_image()
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['groups'] = [{'id': i.id, 'name': i.name}
                          for i in self.groups.all()]
        item['last_login'] = None if self.last_login is None else self.last_login.strftime(
            '%Y-%m-%d')
        return item

    def generate_token_email(self):
        return str(uuid.uuid4())

    def get_image(self):
        if self.image:
            return f'{settings.MEDIA_URL}{self.image}'
        return f'{settings.STATIC_URL}img/src/empty.png'

    def create_or_update_password(self, password):
        if self.pk is None:
            self.set_password(password)
        else:
            user = User.objects.get(pk=self.pk)
            if user.password != password:
                self.set_password(password)

    def set_group_session(self):
        try:
            request = get_current_request()
            groups = request.user.groups.all()
            if groups:
                if 'group' not in request.session:
                    request.session['group'] = groups[0]
        except:
            pass

    def has_at_least_one_group(self):
        return self.groups.all().count() > 0

    def has_more_than_one_group(self):
        return self.groups.all().count() > 1

    def is_customer(self):
        return hasattr(self, 'customer')

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['id']
