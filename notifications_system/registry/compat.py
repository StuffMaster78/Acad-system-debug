from __future__ import annotations
import copy

def _as_list(data):
    if isinstance(data, dict):
        return [{**v, "event_key": k} if "event_key" not in v else v
                for k, v in data.items()]
    return list(data or [])

def _strip_wrappers(x: dict) -> None:
    for k in ("$schema", "events"):
        if isinstance(x, dict):
            x.pop(k, None)

def normalize_broadcast(data):
    """Root array. Required: event_key, description, scope, channels."""
    out = []
    for item in _as_list(data):
        x = copy.deepcopy(item or {})
        _strip_wrappers(x)
        x["event_key"] = x.get("event_key") or x.get("key")
        x["description"] = x.get("description", "")
        x["scope"] = x.get("scope", "systemwide")
        x["channels"] = x.get("channels") or x.get("default_channels") or []
        # remove extras your schema likely rejects
        for bad in ("force_send", "filters", "priority", "forced_channels",
                    "default_channels", "key"):
            x.pop(bad, None)
        out.append(x)
    return out

def normalize_digest(data):
    """Root array. Required: event_key, channels, interval, group_by, digest."""
    out = []
    for item in _as_list(data):
        x = copy.deepcopy(item or {})
        _strip_wrappers(x)
        x["event_key"] = x.get("event_key") or x.get("key")
        x["channels"] = x.get("channels", ["email"])
        x["interval"] = x.get("interval", "weekly")
        x["group_by"] = x.get("group_by", "user_id")
        x["digest"] = x.get("digest") or {
            "merge_strategy": "list_append",
            "max_items": 20
        }
        for bad in ("title", "template", "key"):
            x.pop(bad, None)
        out.append(x)
    return out

def normalize_notifications(data):
    """Root array. Required per item: key, label, enabled, roles, priority, templates."""
    items = _as_list(data)
    out = []
    if isinstance(data, dict):
        kv_iter = data.items()
    else:
        kv_iter = [(None, i) for i in items]
    for k, raw in kv_iter:
        x = copy.deepcopy(raw or {})
        key = x.get("key") or x.get("event_key") or k
        x["key"] = key
        x["event_key"] = x.get("event_key") or key
        x["label"] = x.get("label") or (key or "").replace(".", " ").replace("_", " ").title()
        x["enabled"] = bool(x.get("enabled", True))
        x["roles"] = x.get("roles", [])
        x["priority"] = x.get("priority", "medium")
        x["templates"] = x.get("templates") or {}
        out.append(x)
    return out