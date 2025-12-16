from django.db import models
import uuid

from config.shared.models.models import AuditDateModel

class Role(AuditDateModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=200, unique=True, blank=True)
    code = models.CharField(max_length=200, unique=True, blank=True)
    description = models.CharField(max_length=500, unique=True)
    state = models.BooleanField(default=True)
