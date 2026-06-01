from __future__ import annotations

from rest_framework.response import Response
from rest_framework.views import APIView

SURFACE_BY_PORTAL_CODE: dict[str, str] = {
    "internal_admin": "staff",
    "writer_portal": "writer",
    "client_portal": "client",
}

ALLOWED_ROLES_BY_SURFACE: dict[str, list[str]] = {
    "staff": ["superadmin", "admin", "editor", "support"],
    "writer": ["writer"],
    "client": ["client"],
}


class PortalContextView(APIView):
    """
    Public endpoint called at frontend boot to establish portal surface.

    Returns the surface type (client/writer/staff), resolved website and
    branding for client domains, payment disclosure config, and the list
    of roles permitted on this surface.

    No rate limit — this is a read-only boot endpoint called once per page
    load by every visitor. Throttling it breaks the SPA for all users.

    Requires no authentication — called before the user has logged in.
    """

    authentication_classes = []
    permission_classes = []
    throttle_classes = [] # no rate limit on a public boot endpoint

    def get(self, request):
        portal = getattr(request, "portal", None)
        website = getattr(request, "website", None)

        # Derive surface from the resolved portal, falling back to client
        # if a website matched (custom client domain without an explicit portal record).
        if portal:
            surface = SURFACE_BY_PORTAL_CODE.get(portal.code, "client")
        elif website:
            surface = "client"
        else:
            surface = "client"

        allowed_roles = ALLOWED_ROLES_BY_SURFACE[surface]

        portal_meta = None
        if portal:
            portal_meta = {"code": portal.code, "name": portal.name}

        website_data = None
        branding_data = None
        payment_disclosure = None

        if website:
            branding = getattr(website, "public_branding", None)

            website_data = {
                "id": website.id,
                "name": website.name,
                "slug": website.slug,
                "domain": website.domain,
            }

            branding_data = {
                "brand_name": getattr(branding, "brand_name", website.name),
                "tagline": getattr(branding, "tagline", ""),
                "logo_url": getattr(branding, "logo_url", ""),
                "favicon_url": getattr(branding, "favicon_url", ""),
                "primary_color": getattr(branding, "primary_color", "#2563eb"),
                "secondary_color": getattr(branding, "secondary_color", "#0f172a"),
                "accent_color": getattr(branding, "accent_color", "#14b8a6"),
            }

            processor = getattr(branding, "payment_processor_name", "")
            descriptor = getattr(branding, "payment_statement_descriptor", "")
            if processor:
                brand_name = getattr(branding, "brand_name", website.name)
                payment_disclosure = {
                    "processor_name": processor,
                    "statement_descriptor": descriptor,
                    "text": (
                        f"Your payment is securely processed by {processor}. "
                        f"Your card or bank statement may show: {descriptor or processor}."
                    ),
                    "pre_payment_notice": (
                        f"You are placing this order with {brand_name}. "
                        f"Payments are securely processed by {processor}, our billing partner. "
                        f"Your card statement may show {descriptor or processor}."
                    ),
                }

        return Response(
            {
                "surface": surface,
                "portal": portal_meta,
                "website": website_data,
                "branding": branding_data,
                "payment_disclosure": payment_disclosure,
                "allowed_roles": allowed_roles,
            }
        )
