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
                "homepage_headline": getattr(branding, "homepage_headline", ""),
                "homepage_subheadline": getattr(branding, "homepage_subheadline", ""),
                "social_twitter_url":   getattr(branding, "social_twitter_url", ""),
                "social_facebook_url":  getattr(branding, "social_facebook_url", ""),
                "social_instagram_url": getattr(branding, "social_instagram_url", ""),
                "social_youtube_url":   getattr(branding, "social_youtube_url", ""),
                "social_tiktok_url":    getattr(branding, "social_tiktok_url", ""),
                "social_linkedin_url":  getattr(branding, "social_linkedin_url", ""),
            }

            processor = getattr(branding, "payment_processor_name", "")
            descriptor = getattr(branding, "payment_statement_descriptor", "")
            if processor:
                brand_name = getattr(branding, "brand_name", website.name)
                disclosure_text = getattr(
                    branding,
                    "payment_client_disclosure_text",
                    "",
                )
                short_text = disclosure_text or (
                    f"Your payment is securely processed by {processor}. "
                    f"Your card or bank statement may show: {descriptor or processor}."
                )
                payment_disclosure = {
                    "processor_name": processor,
                    "processor_display_name": processor,
                    "statement_descriptor": descriptor,
                    "client_disclosure_text": disclosure_text,
                    "support_contact": getattr(branding, "payment_support_contact", ""),
                    "requires_acknowledgement": getattr(
                        branding,
                        "payment_requires_acknowledgement",
                        True,
                    ),
                    "text": short_text,
                    "pre_payment_notice": disclosure_text or (
                        f"You are placing this order with {brand_name}. "
                        f"Payments are securely processed by {processor}, our billing partner. "
                        f"Your card statement may show {descriptor or processor}."
                    ),
                }

        # Resolve SEO fields from TenantSEOSettings (Wagtail site setting)
        ga4_measurement_id = None
        promo_bar = None
        og_image_url = None
        schema_org_logo_url = None
        schema_org_name = None
        if website:
            try:
                from wagtail.models import Site as WagtailSite
                from cms_core.models import TenantSEOSettings
                hostname = website.domain.replace("https://", "").replace("http://", "").split("/")[0]
                wagtail_site = WagtailSite.objects.filter(hostname__iexact=hostname).first()
                if wagtail_site:
                    seo = TenantSEOSettings.for_site(wagtail_site)

                    def _img_url(fk, spec="original"):
                        if not fk:
                            return None
                        try:
                            return fk.get_rendition(spec).url
                        except Exception:
                            return getattr(getattr(fk, "file", None), "url", None)

                    ga4_measurement_id = getattr(seo, "google_analytics_id", None) or None
                    og_image_url       = _img_url(getattr(seo, "default_og_image", None), "width-1200")
                    schema_org_logo_url = _img_url(getattr(seo, "schema_org_logo", None), "max-512x512")
                    schema_org_name    = getattr(seo, "schema_org_name", None) or None
                    promo_bar = {
                        "enabled": getattr(seo, "promo_bar_enabled", True),
                        "code":    getattr(seo, "promo_code", "") or "",
                        "message": getattr(seo, "promo_message", "") or "",
                        "suffix":  getattr(seo, "promo_suffix", "") or "",
                    }
            except Exception:
                pass

        return Response(
            {
                "surface": surface,
                "portal": portal_meta,
                "website": website_data,
                "branding": branding_data,
                "payment_disclosure": payment_disclosure,
                "allowed_roles": allowed_roles,
                "ga4_measurement_id": ga4_measurement_id,
                "promo_bar": promo_bar,
                "seo": {
                    "og_image_url":        og_image_url,
                    "schema_org_logo_url": schema_org_logo_url,
                    "schema_org_name":     schema_org_name,
                },
            }
        )
