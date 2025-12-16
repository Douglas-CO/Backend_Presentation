from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
import uuid
from config.shared.models.models import AuditDateModel


class CustomUserManager(UserManager):
    def _create_user(self, email, password, username, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin, AuditDateModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=200, unique=True, null=True)
    razon_social = models.CharField(max_length=200, blank=True, null=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        ordering = ["-created_at"]
