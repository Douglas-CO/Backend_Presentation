import uuid as _uuid
from decimal import Decimal
from datetime import datetime, date

from config.shared.helpers.request_netinfo import get_request_netinfo


def _json_sanitize(v):
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    if isinstance(v, Decimal):
        return float(v)
    return v


def _clean_extra(extra):
    if not extra:
        return {}
    out = {}
    for k, v in extra.items():
        try:
            out[k] = _json_sanitize(v)
        except Exception:
            out[k] = str(v)
    return out


def build_audit_payload(
    *, request, action: str, resource: str,
    description=None, resource_id=None,
    customer_full_name=None, service_line_uuid=None,
    extra=None, http_status=None,
    method=None, route=None, full_path=None, is_sensitive=False,
):
    user = getattr(request, "user", None)
    net = get_request_netinfo(request)
    ip = net.get("client_ip")
    ua = net.get("user_agent") or getattr(
        getattr(request, "META", {}), "HTTP_USER_AGENT", "")
    coords = net.get("coords")
    edge_ip = net.get("edge_ip")
    ip_chain = net.get("ip_chain") or []

    payload = {
        "uuid": str(_uuid.uuid4()),
        "@timestamp": None,  # lo setea el task si viene None
        "event": {
            "action": action,
        },
        "resource": resource,
        "resource_id": str(resource_id) if resource_id else None,
        "description": description,
        "schema_name": getattr(getattr(request, "tenant", None), "schema_name", None),
        "user_id": getattr(user, "id", None),
        "user_uuid": getattr(user, "uuid", None),
        "username": getattr(user, "username", None),
        "user_agent": ua,
        "customer_full_name": customer_full_name,
        "service_line_uuid": str(service_line_uuid) if service_line_uuid else None,
        "extra": _clean_extra(extra),

        "method": method,
        "route": route,
        "full_path": full_path,
        "is_sensitive": is_sensitive,

        # ECS-ish:
        "http": {
            "request": {
                "method": request.method
            },
            "response": {
                "status_code": http_status
            }
        },
        "url": {
            "path": request.path
        },
        "geo": {
            "coordinates": coords
        }
    }
    if ip:
        payload["ip"] = ip
    return payload
