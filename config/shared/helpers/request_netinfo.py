from ipaddress import ip_address
from typing import Dict, List


def _parse_ip_list(xff: str) -> List[str]:
    if not xff:
        return []
    parts = [p.strip() for p in xff.split(",") if p.strip()]
    out = []
    for p in parts:
        try:
            ip_address(p)
            out.append(p)
        except ValueError:
            continue
    return out


def get_request_netinfo(request) -> Dict[str, object]:
    meta = getattr(request, "META", {}) or {}

    xff_raw = meta.get("HTTP_X_FORWARDED_FOR", "") or ""
    ip_chain = _parse_ip_list(xff_raw)

    edge_ip = meta.get("REMOTE_ADDR")

    client_ip = ip_chain[0] if ip_chain else (
        meta.get("HTTP_X_REAL_IP") or edge_ip)

    user_agent = meta.get("HTTP_X_OS") or meta.get(
        "HTTP_USER_AGENT") or "unknown"

    lat, lng = meta.get("HTTP_X_GEO_LAT"), meta.get("HTTP_X_GEO_LNG")
    coords = f"{lat},{lng}" if lat and lng else None

    proto = meta.get("HTTP_X_FORWARDED_PROTO") or meta.get(
        "wsgi.url_scheme") or "http"
    host = meta.get("HTTP_X_FORWARDED_HOST") or meta.get(
        "HTTP_HOST") or meta.get("SERVER_NAME")

    return {
        "client_ip": client_ip,
        "edge_ip": edge_ip,
        "ip_chain": ip_chain,
        "user_agent": user_agent,
        "coords": coords,
        "proto": proto,
        "host": host,
    }
