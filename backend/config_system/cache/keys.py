from __future__ import annotations


def build_config_cache_key(
    key: str,
    user_id: int | None = None,
    tenant_id: int | None = None,
    website_id: int | None = None,
) -> str:
    base = f"config:{key}"
    if user_id is not None:
        return f"{base}:user:{user_id}"
    if tenant_id is not None:
        return f"{base}:tenant:{tenant_id}"
    if website_id is not None:
        return f"{base}:website:{website_id}"
    return f"{base}:global"


def build_kill_switch_cache_key(
    level: str,
    key: str | None = None,
    scope: str | None = None,
    scope_id: int | None = None,
) -> str:

    base = "kill_switch"

    if level == "global":
        return f"{base}:global"

    if level == "feature":
        return f"{base}:feature:{key}"

    if level == "scoped":
        return f"{base}:{scope}:{scope_id}:{key}"

    return f"{base}:unknown"