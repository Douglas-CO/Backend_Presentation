import uuid
from django.db import models

from config.shared.models.models import AuditDateModel


class WebhookLog(AuditDateModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # data that was received by the webhook
    source_name = models.CharField(
        max_length=100, default="SWITCH_PAGOS")  # like tipe
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payload = models.JSONField(blank=True, null=True)

    # http status that was returned by the webhook
    response_status = models.IntegerField(blank=True, null=True)
    response_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"WebhookLog {self.id} (tx_id={self.transaction_id})"
