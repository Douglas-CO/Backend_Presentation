from webhooks.context import build_audit_payload
from collections.abc import Mapping, Sequence
from django.forms.models import model_to_dict
import json


class AuditLogMixin:
    # ---------- config de exclusión ----------
    def _audit_exclude_keys(self):
        # puedes overridear esto en una vista concreta si quieres
        return {
            "id", "pk", "uuid",
            "created_at", "updated_at", "modified_at",
            "date_joined", "last_login",
            "created_by", "modified_by",
            "_state",
        }

    def _audit_exclude_suffixes(self):
        # ignora todo lo que termine en "_at" (fechas tipo auto_now) por defecto
        return ("_at",)

    # ---------- helpers de contexto ----------
    def _model_name(self):
        try:
            if hasattr(self, "service") and hasattr(self.service, "repository"):
                return self.service.repository.model.__name__
        except Exception:
            pass
        return getattr(self, "_model_name_label", self.__class__.__name__)

    def _resource_label(self):
        try:
            if hasattr(self, "service") and hasattr(self.service, "repository"):
                return self.service.repository.model._meta.label
        except Exception:
            pass
        return getattr(self, "_model_name_label", self.__class__.__name__)

    def _username(self, request):
        try:
            return getattr(request.user, "username", None) or str(request.user)
        except Exception:
            return "anonymous"

    def _extract_rid(self, obj, fallback=None):
        rid = None
        try:
            if isinstance(obj, dict):
                rid = obj.get("id") or obj.get("pk") or obj.get("uuid")
            else:
                rid = getattr(obj, "id", None) or getattr(
                    obj, "pk", None) or getattr(obj, "uuid", None)
        except Exception:
            pass
        return rid or fallback

    # ---------- description automático ----------
    def _action_verb(self, action, failed=False):
        mapping = {"CREATE": "CREACION", "UPDATE": "ACTUALIZACION",
                   "DELETE": "ELIMINACION", "PATCH": "ACTUALIZACION"}
        base = mapping.get(action.split()[0], action.upper())
        return f"ERROR AL {base}" if failed else base

    def _extract_validation_error_message(self, e):
        try:
            if hasattr(e, "fields") and e.fields:
                parts = []
                for field, errors in e.fields:
                    for err in errors:
                        parts.append(f"{field}: {err}")
                if parts:
                    return ", ".join(parts)
        except Exception:
            pass
        try:
            detail = getattr(e, "detail", None)
            if isinstance(detail, Mapping):
                parts = []
                for f, errs in detail.items():
                    if isinstance(errs, Sequence) and not isinstance(errs, (str, bytes)):
                        for err in errs:
                            parts.append(f"{f}: {err}")
                    else:
                        parts.append(f"{f}: {errs}")
                if parts:
                    return ", ".join(map(str, parts))
            elif isinstance(detail, Sequence) and not isinstance(detail, (str, bytes)):
                return ", ".join(map(str, detail))
            elif detail:
                return str(detail)
        except Exception:
            pass
        return str(e)

    def _build_description(self, request, *, action, failed=False, error_message=None):
        model = self._model_name()
        user = self._username(request)
        verb = self._action_verb(action, failed=failed)
        if failed:
            msg = error_message or "Error desconocido"
            return f"{verb} {model} POR {user}::: {msg}"
        return f"{verb} {model} POR {user}"

    # ---------- normalizadores/diff ----------
    def _norm(self, v):
        try:
            if isinstance(v, (Mapping, list, tuple)):
                return json.dumps(v, ensure_ascii=False, sort_keys=True)
            return v
        except Exception:
            return str(v)

    def _truncate(self, v, max_len=500):
        s = str(v)
        return (s[:max_len] + "…") if len(s) > max_len else s

    def _to_dict(self, obj):
        if isinstance(obj, Mapping):
            return dict(obj)
        try:
            # si tienes service.serialize, mejor mantener formato igual al de respuesta
            if hasattr(self, "service") and hasattr(self.service, "serialize"):
                d = self.service.serialize(obj)
                if isinstance(d, Mapping):
                    return dict(d)
        except Exception:
            pass
        try:
            # model instance
            return model_to_dict(obj)
        except Exception:
            pass
        try:
            return dict(getattr(obj, "__dict__", {}))
        except Exception:
            return {}

    def _compute_changes_pre_post(self, request_data, pre_dict, post_dict):
        exclude_keys = self._audit_exclude_keys()
        exclude_suffixes = self._audit_exclude_suffixes()

        # normaliza inputs
        req = request_data if isinstance(
            request_data, Mapping) else dict(request_data)
        pre = pre_dict if isinstance(pre_dict, Mapping) else {}
        post = post_dict if isinstance(post_dict, Mapping) else {}

        # solo llaves que están en request y en ambos snapshots
        common = (set(req.keys()) & set(pre.keys()) & set(post.keys()))
        changes = {}
        for k in sorted(common):
            if k in exclude_keys or any(k.endswith(suf) for suf in exclude_suffixes):
                continue
            a = self._norm(pre.get(k))
            b = self._norm(post.get(k))
            if a != b:
                changes[k] = {
                    "from": self._truncate(a),
                    "to":   self._truncate(b),
                }
        return changes

    def _audit_safe(self, request, *, action, description, resource_id=None, extra=None, outcome="SUCCESS"):
        return
        try:
            req_info = self._get_request_info(request)
            payload = build_audit_payload(
                request=request,
                action=action,
                resource=self._resource_label(),
                description=description,
                resource_id=resource_id,
                extra={**(extra or {}), "outcome": outcome},
                method=req_info.get("method"),
                route=req_info.get("route"),
                full_path=req_info.get("full_path"),
            )
            _sa(payload)  # no bloquea la request si falla; retorna bool
        except Exception:
            # no romper la request por audit
            pass

    # ---------- shortcuts ----------
    def audit_create_success(self, request, serialized_instance):
        rid = self._extract_rid(serialized_instance)
        desc = self._build_description(request, action="CREATE", failed=False)
        self._audit_safe(
            request,
            action="CREATE",
            description=desc,
            resource_id=rid,
            extra={"payload_keys": list(getattr(request, "data", {}).keys())},
            outcome="SUCCESS",
        )

    def audit_create_failed(self, request, e):
        msg = self._extract_validation_error_message(e)
        desc = self._build_description(
            request, action="CREATE", failed=True, error_message=msg)
        self._audit_safe(
            request,
            action="CREATE FAILED",
            description=desc,
            extra={"payload_keys": list(
                getattr(request, "data", {}).keys()), "error": str(e)},
            outcome="FAILED",
        )

    # >>> usa 'pre_snapshot' para calcular cambios correctos
    def audit_update_success_prepost(self, request, serialized_instance, *, pre_snapshot, pk=None):
        rid = self._extract_rid(serialized_instance, fallback=pk)
        desc = self._build_description(request, action="UPDATE", failed=False)
        post_snapshot = self._to_dict(serialized_instance)
        changes = self._compute_changes_pre_post(
            getattr(request, "data", {}), pre_snapshot, post_snapshot)
        extra = {"payload_keys": list(getattr(request, "data", {}).keys())}
        if changes:
            extra["changes"] = changes
        self._audit_safe(
            request, action="UPDATE", description=desc, resource_id=rid, extra=extra, outcome="SUCCESS"
        )

    def audit_update_failed(self, request, e, *, pk=None):
        msg = self._extract_validation_error_message(e)
        desc = self._build_description(
            request, action="UPDATE", failed=True, error_message=msg)
        self._audit_safe(
            request,
            action="UPDATE FAILED",
            description=desc,
            resource_id=pk,
            extra={"payload_keys": list(
                getattr(request, "data", {}).keys()), "error": str(e)},
            outcome="FAILED",
        )

    def audit_delete_success(self, request, *, pk=None):
        desc = self._build_description(request, action="DELETE", failed=False)
        self._audit_safe(request, action="DELETE",
                         description=desc, resource_id=pk, outcome="SUCCESS")

    def audit_delete_failed(self, request, e, *, pk=None):
        msg = self._extract_validation_error_message(e)
        desc = self._build_description(
            request, action="DELETE", failed=True, error_message=msg)
        self._audit_safe(
            request, action="DELETE FAILED", description=desc, resource_id=pk, extra={"error": str(e)}, outcome="FAILED"
        )

    # get method, route, full_path from request
    def _get_request_info(self, request):
        return {
            "method": request.method,
            "route": request.resolver_match.route if hasattr(request, "resolver_match") else None,
            "full_path": request.get_full_path() if hasattr(request, "get_full_path") else request.path,
        }
