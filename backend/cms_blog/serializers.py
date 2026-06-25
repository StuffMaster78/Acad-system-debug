"""
Blog API serializers.

Used by:
- Wagtail API v2 custom fields
- Schema.org BlogPosting JSON-LD generation
- Frontend BFF endpoints
"""

from rest_framework import serializers

from cms_authors.serializers import AuthorMinimalSerializer, AuthorSchemaOrgSerializer


class BlogPostListSerializer(serializers.Serializer):
    """Compact blog post for listing pages and related-posts blocks."""

    def to_representation(self, page) -> dict:
        data = {
            "id": page.pk,
            "title": page.title,
            "slug": page.slug,
            "url": getattr(page, "frontend_url", None) or page.url,
            "excerpt": getattr(page, "excerpt", ""),
            "first_published_at": page.first_published_at,
            "last_published_at": page.last_published_at,
        }

        # Author
        author = getattr(page, "primary_author", None)
        if author:
            data["author"] = {
                "name": author.name,
                "slug": author.slug,
                "credentials": author.credentials,
            }

        # Category
        category = getattr(page, "category", None)
        if category:
            data["category"] = {
                "name": category.name,
                "slug": category.slug,
            }

        # Featured image
        featured = getattr(page, "featured_image", None)
        if featured:
            try:
                webp = featured.get_rendition("fill-800x450|format-webp")
                fallback = featured.get_rendition("fill-800x450")
                data["featured_image"] = {
                    "url": webp.url,
                    "url_fallback": fallback.url,
                    "width": 800,
                    "height": 450,
                    "alt": featured.title,
                }
            except Exception:
                data["featured_image"] = None

        # Computed properties
        if hasattr(page, "word_count"):
            data["word_count"] = page.word_count
        if hasattr(page, "reading_time"):
            data["reading_time"] = page.reading_time

        return data


class BlogPostDetailSerializer(serializers.Serializer):
    """Full blog post for detail view — includes body, TOC, references."""

    def to_representation(self, page) -> dict:
        data = BlogPostListSerializer().to_representation(page)

        # Full author
        author = getattr(page, "primary_author", None)
        if author:
            data["author"] = AuthorMinimalSerializer(author).data

        # Contributing authors
        contributing = getattr(page, "contributing_authors", None)
        if contributing:
            data["contributing_authors"] = AuthorMinimalSerializer(
                contributing.all(), many=True
            ).data

        # Tags
        tags = getattr(page, "tags", None)
        if tags:
            data["tags"] = [
                {"name": t.name, "slug": t.slug} for t in tags.all()
            ]

        # Funnel routing
        service = getattr(page, "primary_service", None)
        if service:
            data["primary_service"] = {
                "id": service.pk,
                "title": service.title,
                "slug": service.slug,
                "url": service.url,
            }

        # Pillar
        pillar = getattr(page, "pillar", None)
        if pillar:
            data["pillar"] = {
                "id": pillar.pk,
                "name": pillar.name,
                "slug": pillar.slug,
            }

        # Citation mode
        data["citation_mode"] = getattr(page, "citation_mode", "none")

        # Freshness
        data["last_substantive_update"] = getattr(
            page, "last_substantive_update", None
        )

        # Lead magnet (staff-selected cheat sheet / resource for this article)
        lead_magnet = getattr(page, "lead_magnet", None)
        if lead_magnet and lead_magnet.status == "published":
            data["lead_magnet"] = {
                "slug": lead_magnet.slug,
                "title": lead_magnet.title,
                "description": lead_magnet.description,
                "gate_type": lead_magnet.gate_type,
            }
        else:
            data["lead_magnet"] = None

        # TOC
        if hasattr(page, "toc"):
            data["toc"] = page.toc

        return data


class BlogPostSchemaOrgSerializer(serializers.Serializer):
    """Schema.org BlogPosting JSON-LD for a blog post page.

    Emitted in the <head> of the public page for crawlers and AI systems.
    """

    def to_representation(self, page) -> dict:
        schema = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": page.title,
            "url": getattr(page, "frontend_url", None) or page.full_url,
            "datePublished": (
                page.first_published_at.isoformat()
                if page.first_published_at
                else None
            ),
            "dateModified": (
                page.last_substantive_update.isoformat()
                if getattr(page, "last_substantive_update", None)
                else (
                    page.last_published_at.isoformat()
                    if page.last_published_at
                    else None
                )
            ),
        }

        # Author
        author = getattr(page, "primary_author", None)
        if author:
            schema["author"] = AuthorSchemaOrgSerializer().to_representation(
                author
            )

        # Featured image — use WebP for schema.org image property
        featured = getattr(page, "featured_image", None)
        if featured:
            try:
                schema["image"] = featured.get_rendition("width-1200|format-webp").url
            except Exception:
                try:
                    schema["image"] = featured.get_rendition("original").url
                except Exception:
                    pass

        # Word count
        if hasattr(page, "word_count"):
            schema["wordCount"] = page.word_count

        # Description
        excerpt = getattr(page, "excerpt", "")
        search_desc = getattr(page, "search_description", "")
        schema["description"] = search_desc or excerpt or ""

        # Article section (from category)
        category = getattr(page, "category", None)
        if category:
            schema["articleSection"] = category.name

        # Citations from references (if any)
        try:
            citations = page.citations.select_related("reference").all()
            if citations.exists():
                schema["citation"] = []
                for citation in citations:
                    ref = citation.reference
                    cite_entry = {
                        "@type": "ScholarlyArticle"
                        if ref.is_peer_reviewed
                        else "Article",
                        "headline": ref.title,
                    }
                    if ref.publication_year:
                        cite_entry["datePublished"] = str(ref.publication_year)
                    if ref.authors:
                        cite_entry["author"] = [
                            {
                                "@type": "Person",
                                "name": f"{a.get('given', '')} {a.get('family', '')}".strip(),
                            }
                            for a in ref.authors
                        ]
                    if ref.journal_name:
                        cite_entry["isPartOf"] = {
                            "@type": "Periodical",
                            "name": ref.journal_name,
                        }
                        if ref.issn:
                            cite_entry["isPartOf"]["issn"] = ref.issn
                    if ref.doi:
                        cite_entry["identifier"] = {
                            "@type": "PropertyValue",
                            "propertyID": "DOI",
                            "value": ref.doi,
                        }
                    schema["citation"].append(cite_entry)
        except Exception:
            pass

        # Publisher (from tenant settings)
        try:
            from cms_core.models import TenantSEOSettings

            site = page.get_site()
            if site:
                seo_settings = TenantSEOSettings.for_site(site)
                if seo_settings.schema_org_name:
                    schema["publisher"] = {
                        "@type": "Organization",
                        "name": seo_settings.schema_org_name,
                    }
                    if seo_settings.schema_org_logo:
                        try:
                            schema["publisher"]["logo"] = {
                                "@type": "ImageObject",
                                "url": seo_settings.schema_org_logo.get_rendition(
                                    "original"
                                ).url,
                            }
                        except Exception:
                            pass
        except Exception:
            pass

        return schema