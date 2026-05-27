from django.conf import settings
from django.core.checks import Warning, register
from django.urls import URLPattern, URLResolver, get_resolver


LEGACY_ROUTE_FRAGMENTS: tuple[str, ...] = ()  # all legacy routes removed


def _iter_route_patterns(patterns, prefix=""):
    for pattern in patterns:
        route = f"{prefix}{pattern.pattern}"
        if isinstance(pattern, URLResolver):
            yield from _iter_route_patterns(pattern.url_patterns, route)
        elif isinstance(pattern, URLPattern):
            yield route


@register()
def legacy_runtime_surface_check(app_configs, **kwargs):
    issues = []

    mounted_legacy_routes = [
        route
        for route in _iter_route_patterns(get_resolver().url_patterns)
        if any(fragment in route for fragment in LEGACY_ROUTE_FRAGMENTS)
    ]
    if mounted_legacy_routes:
        issues.append(
            Warning(
                "Legacy wallet/order-file API routes are mounted.",
                hint=(
                    "Use /api/v1/wallets/ and /api/v1/files/ as the public "
                    "contract. Keep wallet/client_wallet/writer_wallet/order_files "
                    "only for migration compatibility."
                ),
                obj=", ".join(mounted_legacy_routes[:5]),
                id="core.W001",
            )
        )

    if getattr(settings, "ENABLE_LEGACY_WRITER_WALLET_SIGNALS", False):
        issues.append(
            Warning(
                "Legacy writer wallet signals are enabled.",
                hint=(
                    "Writer wallet side effects should flow through wallets and "
                    "writer_compensation unless a migration/backfill explicitly "
                    "requires the legacy signals."
                ),
                id="core.W002",
            )
        )

    return issues
