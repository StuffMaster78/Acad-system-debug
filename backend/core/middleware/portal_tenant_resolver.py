from __future__ import annotations

from urllib.parse import urlsplit

from django.db.models import Q
from django.utils.deprecation import MiddlewareMixin

from accounts.models.portal_definition import PortalDefinition
from websites.models.websites import Website


def _domain_candidates(host: str) -> list[str]:
    """
    Match both bare host values and URLField-style domains.

    Website.domain historically stores values like https://example.com, while
    request.get_host() returns example.com. Keep both forms resolvable so
    portal boot works across local, staged, and production tenants.
    """
    normalized = host.lower().strip().removeprefix("www.")
    return [
        normalized,
        f"www.{normalized}",
        f"https://{normalized}",
        f"https://www.{normalized}",
        f"http://{normalized}",
        f"http://www.{normalized}",
    ]


def _domain_query(field: str, candidates: list[str]) -> Q:
    query = Q()
    for candidate in candidates:
        query |= Q(**{f"{field}__iexact": candidate})
    return query


def _host_from_domain(value: str) -> str:
    parsed = urlsplit(value if "://" in value else f"//{value}")
    return (parsed.hostname or value).lower().removeprefix("www.")


class PortalTenantResolverMiddleware(MiddlewareMixin):
    """
    Resolves request.portal and request.website from the request host.
    """

    def process_request(self, request):
        host = _host_from_domain(request.get_host().split(":")[0])
        candidates = _domain_candidates(host)

        request.portal = None
        request.website = None

        # Resolve portal by exact domain match
        portal = PortalDefinition.objects.filter(
            _domain_query("domain", candidates),
            is_active=True,
        ).first()

        if portal:
            request.portal = portal

        # Resolve website (tenant) — try exact host first, then parent domain.
        # The parent-domain fallback lets portal SPAs on app.* subdomains resolve
        # their tenant's branding: app.gradecrest.com → gradecrest.com Website.
        website = Website.objects.filter(
            _domain_query("domain", candidates),
            is_active=True,
            is_deleted=False,
        ).first()

        if website is None:
            parts = host.split(".")
            if len(parts) > 2:
                parent = ".".join(parts[1:])
                website = Website.objects.filter(
                    _domain_query("domain", _domain_candidates(parent)),
                    is_active=True,
                    is_deleted=False,
                ).first()

        if website:
            request.website = website

        # Fallback mapping — kick in if domain lookup above misses (e.g. DB not yet seeded)
        if not request.portal:
            if host in ("admin.writerscreek.com",):
                request.portal = PortalDefinition.objects.filter(
                    code="internal_admin"
                ).first()
            elif host in ("writerscreek.com", "www.writerscreek.com"):
                request.portal = PortalDefinition.objects.filter(
                    code="writer_portal"
                ).first()
