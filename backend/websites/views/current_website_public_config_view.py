from __future__ import annotations

from rest_framework.response import Response
from rest_framework.views import APIView

from websites.models.websites import Website


class CurrentWebsitePublicConfigView(APIView):
    """
    Return public config for the website resolved from the request host.
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        host = request.get_host().split(":")[0].lower()

        website = Website.objects.filter(
            domain__iexact=host,
            is_active=True,
        ).first()

        if website is None:
            return Response(
                {
                    "detail": "Website not found.",
                    "host": host,
                },
                status=404,
            )

        branding = getattr(website, "public_branding", None)
        niche = getattr(website, "niche", None)
        settings = website.website_settings.first()

        return Response(
            {
                "website": {
                    "id": website.id,
                    "name": website.name,
                    "slug": website.slug,
                    "domain": website.domain,
                },
                "branding": {
                    "brand_name": getattr(branding, "brand_name", website.name),
                    "tagline": getattr(branding, "tagline", ""),
                    "logo_url": getattr(branding, "logo_url", ""),
                    "favicon_url": getattr(branding, "favicon_url", ""),
                    "primary_color": getattr(
                        branding,
                        "primary_color",
                        "#2563eb",
                    ),
                    "secondary_color": getattr(
                        branding,
                        "secondary_color",
                        "#0f172a",
                    ),
                    "accent_color": getattr(
                        branding,
                        "accent_color",
                        "#14b8a6",
                    ),
                    "trust_claims": getattr(branding, "trust_claims", []),
                },
                "niche": {
                    "niche_type": getattr(
                        niche,
                        "niche_type",
                        "general_academic",
                    ),
                    "service_catalog": getattr(niche, "service_catalog", []),
                    "subject_catalog": getattr(niche, "subject_catalog", []),
                    "order_form_defaults": getattr(
                        niche,
                        "order_form_defaults",
                        {},
                    ),
                    "seo_defaults": getattr(niche, "seo_defaults", {}),
                },
                "contact": {
                    "support_email": getattr(settings, "support_email", ""),
                    "from_email": getattr(settings, "from_email", ""),
                    "no_reply_email": getattr(settings, "no_reply_email", ""),
                },
            }
        )