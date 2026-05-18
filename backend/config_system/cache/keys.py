from __future__ import annotations


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