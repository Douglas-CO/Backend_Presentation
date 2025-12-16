import json
import os
import threading
import time
import pika
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


_AMQP_URL = os.getenv(
    "AUDIT_AMQP_URL",
    "amqp://audit_user:audit_pass@rabbitmq:5672/%2Ferp-audit"
)
_EXCHANGE = os.getenv("AUDIT_EXCHANGE", "audit")
_ROUTING_KEY = os.getenv("AUDIT_ROUTING_KEY", "audit.logs")

_PUBLISH_CONFIRMS = os.getenv(
    "AUDIT_PUBLISH_CONFIRMS", "false").lower() == "true"
_PUBLISH_TIMEOUT = float(os.getenv("AUDIT_PUBLISH_TIMEOUT", "0.25"))
_RETRY_MAX = int(os.getenv("AUDIT_PUBLISH_RETRY_MAX", "3"))

_lock = threading.Lock()
_connection: Optional[pika.BlockingConnection] = None
_channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None


def _json_default(o):
    """Conversor para tipos comunes no serializables por JSON nativo"""
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    if isinstance(o, Decimal):
        return float(o)
    if isinstance(o, UUID):
        return str(o)
    if hasattr(o, "dict"):
        return o.dict()
    if hasattr(o, "model_dump"):
        return o.model_dump()
    if hasattr(o, "__dict__"):
        return o.__dict__
    return str(o)  # último recurso


def _to_body(payload):
    """Convierte el payload a JSON bytes seguro"""
    try:
        return json.dumps(payload, default=_json_default, ensure_ascii=False).encode("utf-8")
    except Exception as e:
        # si no se puede serializar, empaquetamos un error controlado
        print("[audit] payload no serializable:", type(payload), e)
        return json.dumps(
            {
                "_serialization_error": str(e),
                "_repr": repr(payload)[:2000],
            },
            ensure_ascii=False
        ).encode("utf-8")
