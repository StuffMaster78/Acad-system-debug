"""
Service page API serializers and Schema.org Service JSON-LD.
"""

from rest_framework import serializers


class ServicePageListSerializer(serializers.Serializer):
    """Compact service page for listings and cross-sell blocks."""

    def to_representation(self, page) -> dict:
        return {
            "id": page.pk,
            "title": page.title,
            "slug": page.slug,
            "url": page.url,
            "pricing_from": str(page.pricing_from) if page.pricing_from else None,
            "pricing_to": str(page.pricing_to) if page.pricing_to else None,
            "turnaround_hours_fastest": page.turnaround_hours_fastest,
            "primary_cta_text": page.primary_cta_text,
            "primary_cta_url": page.primary_cta_url,
        }


class ServicePageSchemaOrgSerializer(serializers.Serializer):
    """Schema.org Service JSON-LD for <head> injection."""

    def to_representation(self, page) -> dict:
        schema = {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": page.title,
            "url": page.full_url,
            "description": (
                page.search_description
                or page.title
            ),
        }

        # Pricing
        if page.pricing_from:
            schema["offers"] = {
                "@type": "Offer",
                "priceCurrency": "USD",
                "price": str(page.pricing_from),
            }
            if page.pricing_to:
                schema["offers"]["highPrice"] = str(page.pricing_to)
                schema["offers"]["@type"] = "AggregateOffer"
                schema["offers"]["lowPrice"] = str(page.pricing_from)

        # Provider (from tenant settings)
        try:
            from cms_core.models import TenantSEOSettings

            site = page.get_site()
            if site:
                seo_settings = TenantSEOSettings.for_site(site)
                if seo_settings.schema_org_name:
                    schema["provider"] = {
                        "@type": "Organization",
                        "name": seo_settings.schema_org_name,
                    }
        except Exception:
            pass

        # Service category
        category = getattr(page, "service_category", None)
        if category:
            schema["serviceType"] = category.name

        # Reviewer
        reviewer = getattr(page, "reviewer", None)
        if reviewer:
            schema["review"] = {
                "@type": "Review",
                "author": {
                    "@type": "Person",
                    "name": reviewer.name,
                },
            }
            if page.last_substantive_update:
                schema["review"]["datePublished"] = (
                    page.last_substantive_update.isoformat()
                )

        return schema