"""Webhook log views."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from django.conf import settings
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError, TransportError

import uuid as _uuid
from datetime import datetime, timezone as _tz

from webhooks.context import build_audit_payload
from config.shared.serializers.common_serializer import CommonSerializerStaticHelper
from webhooks.serializers.auditoria_log_serializers import (
    AuditLogCreateSerializer
)


class ESLogService:
    """
    Servicio de búsqueda/lectura para índices de auditoría.
    - Index pattern:  f"{ES_INDEX_PREFIX}-*"
    - Alias de escritura recomendado: "audit-write" (para ILM)
    - Campos clave:    @timestamp, event.action, event.outcome, user.id, source.ip
    """

    def __init__(self, *, timeout: int = 10):
        self.timeout = timeout
        self.es = self._build_client()

    # ---------------------------
    # Client & indices utilities
    # ---------------------------
    def _build_client(self) -> Elasticsearch:
        kwargs: Dict[str, Any] = {"request_timeout": self.timeout}
        if getattr(settings, "ES_USER", None):
            kwargs["basic_auth"] = (settings.ES_USER, settings.ES_PASS)
        return Elasticsearch(settings.ES_URL, **kwargs)

    def _indices(self) -> str:
        return f"{settings.ES_INDEX_PREFIX}-*"

    def ping(self) -> bool:
        try:
            return bool(self.es.ping())
        except Exception:
            return False

    # ---------------------------
    # Query composition
    # ---------------------------
    def _build_query_and_sort(
        self,
        params: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Mapea tus parámetros (de AuditLogQuerySerializer) a una query v8.
        Soporta:
          - q (multi_match)
          - action -> event.action
          - resource, username, schema_name, status, resource_id (term)
          - user_id -> user.id (term)
          - date_from/date_to -> range @timestamp
          - sort -> @timestamp asc|desc
        """
        must: List[Dict[str, Any]] = []
        filters: List[Dict[str, Any]] = []

        # Búsqueda de texto
        q = params.get("q")
        if q:
            must.append({
                "multi_match": {
                    "query": q,
                    "fields": [
                        "description^2",
                        "resource",
                        "username",
                        "customer_full_name",
                        "extra.*"
                    ],
                    "type": "best_fields"
                }
            })

        # Mapeo de exact-match (terms)
        term_map = {
            "action":      "event.action",
            "resource":    "resource",
            "username":    "username",
            "schema_name": "schema_name",
            "resource_id": "resource_id",
        }
        for p_key, es_field in term_map.items():
            val = params.get(p_key)
            if val not in (None, ""):
                filters.append({"term": {es_field: val}})

        # user_id -> user.id
        if params.get("user_id") is not None:
            try:
                uid = int(params["user_id"])
                filters.append({"term": {"user.id": uid}})
            except (TypeError, ValueError):
                # ignora si no es entero
                pass

        # Rango de tiempo sobre @timestamp
        if params.get("date_from") or params.get("date_to"):
            rng: Dict[str, Any] = {}
            if params.get("date_from"):
                rng["gte"] = params["date_from"].isoformat()
            if params.get("date_to"):
                rng["lte"] = params["date_to"].isoformat()
            filters.append({"range": {"@timestamp": rng}})

        query = {
            "bool": {
                "must": must or [{"match_all": {}}],
                "filter": filters
            }
        }

        # Orden
        sort_param = params.get("sort", "-timestamp")
        order = "desc" if sort_param == "-timestamp" else "asc"
        sort = [{"@timestamp": {"order": order}}]

        return query, sort

    # ---------------------------
    # Adapter: ECS -> shape plano esperado por tu serializer
    # ---------------------------

    def _adapt_source(self, h: Dict[str, Any]) -> Dict[str, Any]:
        src = (h.get("_source") or {}).copy()

        # timestamp
        ts = src.get("@timestamp") or src.get("timestamp")
        if ts:
            src["timestamp"] = ts  # tu serializer espera 'timestamp'

        # action
        if "action" not in src:
            ev = src.get("event") or {}
            if ev.get("action"):
                src["action"] = ev["action"]

        # ip
        if "ip" not in src:
            src_ip = (src.get("client") or {}).get("ip")
            if src_ip:
                src["ip"] = src_ip

        # user_id / user_uuid / username
        u = src.get("user") or {}
        if "user_id" not in src and u.get("id") is not None:
            src["user_id"] = u.get("id")
        if "user_uuid" not in src and u.get("uuid"):
            src["user_uuid"] = u.get("uuid")
        if "username" not in src and u.get("name"):
            src["username"] = u.get("name")

        # resource_id a string
        if src.get("resource_id") is not None:
            src["resource_id"] = str(src["resource_id"])

        # id/index útiles para depurar
        _id = h.get("_id")
        _index = h.get("_index")
        extra = src.get("extra") or {}
        # (opcional) inyecta la metadata del hit en extra
        extra.setdefault("_hit", {})
        if _id:
            extra["_hit"]["_id"] = _id
            if 'uuid' not in src:
                src['uuid'] = _id  # fallback
        if _index:
            extra["_hit"]["_index"] = _index
        src["extra"] = extra

        return src

    # ---------------------------
    # Standard search (from/size)
    # ---------------------------

    def search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query, sort = self._build_query_and_sort(params)
        offset = int(params.get("offset", 0))
        size = int(params.get("limit", 50))

        res = self.es.search(
            index=self._indices(),
            query=query,
            from_=offset,
            size=size,
            sort=sort
        )
        hits = res.get("hits", {}).get("hits", [])
        total = res.get("hits", {}).get("total", {}).get("value", 0)

        items = [self._adapt_source(h) for h in hits]  # <- normaliza aquí
        return {"total": total, "items": items}

    # --------------------------------------------
    # Streaming search: PIT + search_after (big)
    # --------------------------------------------
    def open_pit(self, keep_alive: str = "2m") -> str:
        pit = self.es.open_point_in_time(
            index=self._indices(),
            keep_alive=keep_alive
        )
        return pit.get("pit_id")

    def close_pit(self, pit_id: str) -> None:
        try:
            self.es.close_point_in_time(body={"pit_id": pit_id})
        except Exception:
            # no rompas flujo si ya expiró
            pass

    def search_stream(
        self,
        params: Dict[str, Any],
        *,
        page_size: int = 500,
        keep_alive: str = "2m",
        pit_id: Optional[str] = None,
        search_after: Optional[List[Any]] = None,
        order: str = "desc"
    ) -> Dict[str, Any]:
        """
        Paginación eficiente para grandes volúmenes.
        Devuelve: items, next_search_after, pit_id
        Convenio: ordenar por @timestamp y _shard_doc
        """
        query, _ = self._build_query_and_sort(
            params)  # reutiliza filtros de negocio
        if pit_id is None:
            pit_id = self.open_pit(keep_alive=keep_alive)

        sort = [
            {"@timestamp": {"order": order}},
            {"_shard_doc": {"order": order}},
        ]

        res = self.es.search(
            size=page_size,
            query=query,
            sort=sort,
            pit={"id": pit_id, "keep_alive": keep_alive},
            search_after=search_after
        )

        hits = res.get("hits", {}).get("hits", [])
        items = [
            (h.get("_source") or {}) | {
                "_id": h.get("_id"), "_index": h.get("_index")}
            for h in hits
        ]

        next_after = hits[-1]["sort"] if hits else None

        return {
            "items": items,
            "next_search_after": next_after,
            "pit_id": pit_id
        }

    # ---------------------------
    # Get by UUID / _id helpers
    # ---------------------------
    def get_by_uuid(self, uuid: str) -> Optional[Dict[str, Any]]:
        # 1) Por _id
        try:
            res = self.es.search(
                index=self._indices(),
                query={"ids": {"values": [uuid]}},
                size=1
            )
            hits = res.get("hits", {}).get("hits", [])
            if hits:
                return self._adapt_source(hits[0])  # <- normaliza
        except TransportError:
            pass

        # 2) Por campo uuid
        try:
            res = self.es.search(
                index=self._indices(),
                query={"term": {"uuid": uuid}},
                size=1,
                sort=[{"@timestamp": {"order": "desc"}}]
            )
            hits = res.get("hits", {}).get("hits", [])
            if hits:
                return self._adapt_source(hits[0])  # <- normaliza
        except TransportError:
            pass

        return None

    def get_by_id(self, index: str, _id: str) -> Optional[Dict[str, Any]]:
        try:
            doc = self.es.get(index=index, id=_id)
            # simula un hit para reutilizar el adaptador
            h = {"_source": doc.get("_source") or {}, "_id": doc.get(
                "_id"), "_index": doc.get("_index")}
            return self._adapt_source(h)
        except NotFoundError:
            return None

    # WRITE METHODS ============================
    def _resolve_uuid(self, request, data: Dict[str, Any]) -> str:
        idem = getattr(request, "META", {}).get("HTTP_IDEMPOTENCY_KEY")
        if idem:
            try:
                return str(_uuid.UUID(idem))
            except Exception:
                pass
        if data.get("uuid"):
            try:
                return str(_uuid.UUID(str(data["uuid"])))
            except Exception:
                pass
        return str(_uuid.uuid4())

    def _inject_trace(self, request, payload: Dict[str, Any]) -> None:
        req_id = getattr(request, "META", {}).get("HTTP_X_REQUEST_ID")
        if req_id:
            extra = payload.get("extra") or {}
            extra.setdefault("trace", {})
            extra["trace"]["request_id"] = req_id
            payload["extra"] = extra

    def write_sync_from_request(self, request, data: Dict[str, Any]) -> Dict[str, Any]:
        valid = CommonSerializerStaticHelper.validate_and_serialize_by_serializer(
            data=data, serializer=AuditLogCreateSerializer
        )

        payload = build_audit_payload(
            request=request,
            action=valid["action"],
            resource=valid["resource"],
            description=valid.get("description"),
            resource_id=valid.get("resource_id"),
            customer_full_name=valid.get("customer_full_name"),
            service_line_uuid=valid.get("service_line_uuid"),
            extra=valid.get("extra"),
            http_status=valid.get("http_status"),
            method=request.method,
            route=getattr(
                getattr(request, "resolver_match", None), "route", None),
            full_path=request.get_full_path() if hasattr(
                request, "get_full_path") else request.path,
            is_sensitive=bool(valid.get("is_sensitive", False)),
        )

        payload["uuid"] = self._resolve_uuid(request, data)

        # 1) Forzar @timestamp (UTC)
        from datetime import datetime, timezone as _tz
        payload["@timestamp"] = data.get("timestamp").isoformat() if data.get(
            "timestamp") else datetime.now(_tz.utc).isoformat()

        if data.get("status"):
            payload["status"] = str(data["status"])
        self._inject_trace(request, payload)

        alias = getattr(settings, "ES_ALIAS_WRITE", None) or "audit-write"

        # 2) Visibilidad inmediata del doc en búsquedas siguientes
        # 3) (Opcional) cambiar "index" -> "create" para idempotencia estricta
        self.es.index(
            index=alias,
            id=payload["uuid"],
            document=payload,
            op_type="index",          # o "create"
            refresh="wait_for"        # <--- clave para que lo veas enseguida
        )

        # (Opcional) devolver el doc tal como quedó
        return {"uuid": payload["uuid"], "written": True, "index": alias}
