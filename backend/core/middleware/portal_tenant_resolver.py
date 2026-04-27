from __future__ import annotations

from django.utils.deprecation import MiddlewareMixin

from accounts.models.portal_definition import PortalDefinition
from websites.models.websites import Website


class PortalTenantResolverMiddleware(MiddlewareMixin):
    """
    Resolves request.portal and request.website from the request host.
    """

    def process_request(self, request):
        host = request.get_host().lower().split(":")[0]

        request.portal = None
        request.website = None

        # Resolve portal by exact domain match
        portal = PortalDefinition.objects.filter(
            domain__iexact=host,
            is_active=True,
        ).first()

        if portal:
            request.portal = portal

        # Resolve website (tenant)
        website = Website.objects.filter(
            domain__iexact=host,
        ).first()

        if website:
            request.website = website

        # Fallback mapping (optional safety)
        if host == "ordermanagement.com":
            request.portal = PortalDefinition.objects.filter(
                code="internal_admin"
            ).first()

        if host == "writers.ordermanagement.com":
            request.portal = PortalDefinition.objects.filter(
                code="writer_portal"
            ).first()