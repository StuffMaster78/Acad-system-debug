"""
Service page API serializers and Schema.org Service JSON-LD.
"""

from rest_framework import serializers


def _decimal_to_str(value):
    return str(value) if value is not None else None


def _stream_items(stream_value) -> list:
    if not stream_value:
        return []
    return [
        _serialize_value(block.value)
        for block in stream_value
        if getattr(block, "block_type", None) == "item"
    ]


def _image_payload(image) -> dict | None:
    if not image:
        return None
    try:
        return {
            "id": image.pk,
            "title": image.title,
            "url": image.get_rendition("width-1600|format-webp").url,
            "url_fallback": image.get_rendition("width-1600").url,
            "full_url": image.get_rendition("original").url,
            "width": 1600,
        }
    except Exception:
        return {
            "id": getattr(image, "pk", None),
            "title": getattr(image, "title", ""),
            "url": getattr(getattr(image, "file", None), "url", None),
        }


def _page_payload(page) -> dict | None:
    if not page:
        return None
    specific = getattr(page, "specific", page)
    return {
        "id": specific.pk,
        "title": specific.title,
        "slug": specific.slug,
        "url": specific.url,
        "description": getattr(specific, "search_description", ""),
    }


def _attachment_payload(attachment) -> dict | None:
    if not attachment:
        return None
    return {
        "id": attachment.pk,
        "title": getattr(attachment, "title", ""),
        "slug": getattr(attachment, "slug", ""),
        "description": getattr(attachment, "description", ""),
        "file_type": getattr(attachment, "file_type", ""),
    }


def _serialize_value(value):
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "source"):
        return value.source
    if hasattr(value, "get_rendition"):
        return _image_payload(value)
    if hasattr(value, "specific") or hasattr(value, "url") and hasattr(value, "title"):
        return _page_payload(value)
    if hasattr(value, "stream_block"):
        return _serialize_stream(value)
    if isinstance(value, dict) or hasattr(value, "items"):
        return {str(k): _serialize_value(v) for k, v in dict(value).items()}
    if isinstance(value, (list, tuple)):
        return [_serialize_value(v) for v in value]
    return str(value)


def _serialize_stream(stream_value) -> list[dict]:
    if not stream_value:
        return []

    blocks = []
    for block in stream_value:
        blocks.append({
            "id": getattr(block, "id", None),
            "type": block.block_type,
            "value": _serialize_value(block.value),
        })
    return blocks


def _faq_blocks(page) -> list[dict]:
    faqs = []
    for block in getattr(page, "body", []) or []:
        if block.block_type != "faq":
            continue
        value = _serialize_value(block.value)
        if value:
            faqs.append({
                "question": value.get("question", ""),
                "answer": value.get("answer", ""),
            })
    return faqs


class ServicePageListSerializer(serializers.Serializer):
    """Compact service page for listings and cross-sell blocks."""

    def to_representation(self, page) -> dict:
        return {
            "id": page.pk,
            "title": page.title,
            "slug": page.slug,
            "url": page.url,
            "template_key": getattr(page, "template_key", "standard_service"),
            "search_description": getattr(page, "search_description", ""),
            "category": {
                "name": page.service_category.name,
                "slug": page.service_category.slug,
            } if getattr(page, "service_category", None) else None,
            "pricing_from": _decimal_to_str(page.pricing_from),
            "pricing_to": _decimal_to_str(page.pricing_to),
            "turnaround_hours_fastest": page.turnaround_hours_fastest,
            "turnaround_hours_standard": page.turnaround_hours_standard,
            "primary_cta_text": page.primary_cta_text,
            "primary_cta_url": page.primary_cta_url,
        }


class ServicePageDetailSerializer(serializers.Serializer):
    """Frontend-friendly service page detail for Nuxt marketing pages."""

    def to_representation(self, page) -> dict:
        data = ServicePageListSerializer().to_representation(page)

        reviewer = getattr(page, "reviewer", None)
        data.update({
            "meta": {
                "seo_title": getattr(page, "seo_title", "") or page.title,
                "search_description": getattr(page, "search_description", ""),
                "first_published_at": page.first_published_at,
                "last_published_at": page.last_published_at,
                "last_substantive_update": getattr(page, "last_substantive_update", None),
            },
            "hero": {
                "headline": page.hero_headline or page.title,
                "subheadline": page.hero_sub or getattr(page, "search_description", ""),
            },
            "includes_items": _stream_items(getattr(page, "includes_items", [])),
            "delivers_items": _stream_items(getattr(page, "delivers_items", [])),
            "who_for": getattr(page, "who_for", ""),
            "body": _serialize_stream(getattr(page, "body", [])),
            "faqs": _faq_blocks(page),
            "reviewer": {
                "name": reviewer.name,
                "slug": reviewer.slug,
                "credentials": reviewer.credentials,
            } if reviewer else None,
        })

        try:
            related = (
                page.__class__.objects.live()
                .sibling_of(page, inclusive=False)
                .select_related("service_category")
                .order_by("title")[:6]
            )
            data["related_services"] = ServicePageListSerializer(related, many=True).data
        except Exception:
            data["related_services"] = []

        data["schema"] = ServicePageSchemaOrgSerializer().to_representation(page)
        return data


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
            if page.pricing_to:
                schema["offers"] = {
                    "@type": "AggregateOffer",
                    "priceCurrency": "USD",
                    "lowPrice": str(page.pricing_from),
                    "highPrice": str(page.pricing_to),
                }
            else:
                schema["offers"] = {
                    "@type": "Offer",
                    "priceCurrency": "USD",
                    "price": str(page.pricing_from),
                }

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

        # Aggregate rating (opt-in per page)
        if getattr(page, "show_aggregate_rating", False):
            try:
                from cms_core.models import TenantSEOSettings
                site = page.get_site()
                if site:
                    seo = TenantSEOSettings.for_site(site)
                    rating_value = getattr(seo, "aggregate_rating_value", None)
                    review_count = getattr(seo, "aggregate_rating_count", None)
                    if rating_value and review_count:
                        schema["aggregateRating"] = {
                            "@type": "AggregateRating",
                            "ratingValue": str(rating_value),
                            "reviewCount": str(review_count),
                            "bestRating": "5",
                            "worstRating": "1",
                        }
            except Exception:
                pass

        # Freshness
        if page.last_substantive_update:
            schema["dateModified"] = page.last_substantive_update.isoformat()
        if page.first_published_at:
            schema["datePublished"] = page.first_published_at.isoformat()

        return schema
