import uuid
from django.db import models

from django.contrib.auth.models import Group

from config.shared.helpers.model_validators_helper import string_array_model_validator


class CustomGroup(Group):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    codigo = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    system_modules = models.JSONField(
        blank=True, null=True, validators=[string_array_model_validator])

    class Meta:
        verbose_name = "Custom Group"
        verbose_name_plural = "Custom Groups"
