from django.db import models
from django.contrib.auth.models import AbstractUser
from backend_simple.permissions_config import GRUPO_SYSTEM_MODULES, GRUPO_PERMISSIONS


class Grupo(models.Model):
    name = models.CharField(max_length=100, unique=True)
    system_modules = models.JSONField(default=list)
    permissions = models.JSONField(default=list)

    def save(self, *args, **kwargs):
        # Validar system_modules
        for mod in self.system_modules:
            if mod not in GRUPO_SYSTEM_MODULES:
                raise ValueError(f"System module inválido: {mod}")

        # Validar permissions
        for perm in self.permissions:
            if perm not in GRUPO_PERMISSIONS:
                raise ValueError(f"Permission inválido: {perm}")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Usuario(AbstractUser):
    grupo = models.ForeignKey(Grupo, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.username
