"""
CMS Core Views
================

API endpoints for content import/paste functionality and content health checks.
"""

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView


class PasteContentView(APIView):
    """POST /cms-api/paste/

    Accept pasted HTML or plain text, return StreamField blocks.

    The editor pastes content into a dialog in the Wagtail admin.
    This endpoint converts it to blocks. The frontend then inserts
    the blocks into the page's StreamField.

    Body:
        {
            "content": "<h2>Introduction</h2><p>Care plans are...</p>",
            "format": "html" // or "text"
        }

    Returns:
        {
            "blocks": [
                {"type": "heading", "value": {"text": "Introduction", "level": "h2"}},
                {"type": "paragraph", "value": "<p>Care plans are...</p>"},
                ...
            ],
            "block_count": 2,
            "word_count": 42
        }
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        content = request.data.get("content", "").strip()
        content_format = request.data.get("format", "html")

        if not content:
            return Response(
                {"error": "content field required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from cms_core.services.content_importer import ContentImporter

        if content_format == "text":
            blocks = ContentImporter.plain_text_to_blocks(content)
        else:
            blocks = ContentImporter.html_to_blocks(content)

        # Count words across all blocks
        from django.utils.html import strip_tags

        word_count = 0
        for block in blocks:
            value = block.get("value", "")
            if isinstance(value, str):
                word_count += len(strip_tags(value).split())
            elif isinstance(value, dict):
                text = value.get("text", "")
                word_count += len(strip_tags(text).split())

        return Response({
            "blocks": blocks,
            "block_count": len(blocks),
            "word_count": word_count,
        })


class ValidateContentView(APIView):
    """POST /cms-api/validate/

    Run validators against a page without publishing.
    Used by the composer's "Check before publish" button.

    Body:
        {"page_id": 123}

    Returns:
        {
            "is_publishable": true,
            "blockers": [],
            "warnings": [...],
            "suggestions": [...]
        }
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        page_id = request.data.get("page_id")

        if not page_id:
            return Response(
                {"error": "page_id required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from wagtail.models import Page

        try:
            page = Page.objects.get(pk=page_id).specific
        except Page.DoesNotExist:
            return Response(
                {"error": "Page not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        from cms_core.validators import validate_page_for_publish

        result = validate_page_for_publish(page)

        # Add internal linking health
        try:
            from cms_content_graph.services.linking_service import (
                InternalLinkingService,
            )

            linking = InternalLinkingService.validate_linking_health(page)
            for warning in linking["warnings"]:
                result.add_suggestion(warning)
        except ImportError:
            pass

        return Response(result.to_dict())


# ---------------------------------------------------------------------------
# Content Health
# ---------------------------------------------------------------------------

class ContentHealthView(APIView):
    """
    GET /cms-api/content-health/

    Scans all live Wagtail pages (blog + service) and published SEO pages for
    the current site/website and returns editorial health flags per item.

    Health flags:
        missing_meta — no search_description / meta_description
        missing_author — blog post with no primary_author
        stale — no substantive update in 90+ days
        no_cta — service page with no primary_cta_text
        no_service_route — blog post not linked to any service page
        no_citations — blog post with citation_style set but no references
    """

    permission_classes = [permissions.IsAuthenticated]

    STALE_DAYS = 90

    def get(self, request):
        from django.utils import timezone
        from datetime import timedelta

        site = getattr(request, "site", None)
        website = getattr(request, "website", None)
        stale_threshold = timezone.now() - timedelta(days=self.STALE_DAYS)

        items = []
        summary: dict[str, int] = {
            "total": 0,
            "healthy": 0,
            "missing_meta": 0,
            "missing_author": 0,
            "stale": 0,
            "no_cta": 0,
            "no_service_route": 0,
            "no_citations": 0,
        }

        # ── Blog posts ────────────────────────────────────────────────────
        try:
            from cms_blog.models import BlogPostPage
            from cms_content_graph.models import BlogServiceLink

            qs = BlogPostPage.objects.live()
            if site:
                qs = qs.filter(locale__isnull=False).in_site(site)

            linked_ids = set(
                BlogServiceLink.objects.values_list("blog_post_id", flat=True)
            )

            for page in qs.select_related("primary_author").iterator():
                flags = []

                if not page.search_description:
                    flags.append("missing_meta")
                if not page.primary_author_id:
                    flags.append("missing_author")

                last_updated = page.last_substantive_update or page.last_published_at
                if last_updated and last_updated < stale_threshold:
                    flags.append("stale")
                elif not last_updated:
                    flags.append("stale")

                if page.pk not in linked_ids:
                    flags.append("no_service_route")

                # Citation style set but no actual references attached
                citation_style = getattr(page, "citation_style", None)
                if citation_style and citation_style != "none":
                    try:
                        if not page.references.exists():
                            flags.append("no_citations")
                    except Exception:
                        pass

                items.append(self._item(page, "blog", flags))
                self._tally(summary, flags)

        except ImportError:
            pass

        # ── Service pages ─────────────────────────────────────────────────
        try:
            from cms_service_pages.models import ServicePage

            qs = ServicePage.objects.live()
            if site:
                qs = qs.in_site(site)

            for page in qs.iterator():
                flags = []

                if not page.search_description:
                    flags.append("missing_meta")
                if not getattr(page, "primary_cta_text", None):
                    flags.append("no_cta")

                last_updated = getattr(page, "last_published_at", None)
                if last_updated and last_updated < stale_threshold:
                    flags.append("stale")

                items.append(self._item(page, "service", flags))
                self._tally(summary, flags)

        except ImportError:
            pass

        # ── SEO pages ─────────────────────────────────────────────────────
        try:
            from seo_pages.models import SeoPage

            qs = SeoPage.objects.filter(is_published=True, is_deleted=False)
            if website:
                qs = qs.filter(website=website)

            for page in qs.iterator():
                flags = []

                if not getattr(page, "meta_description", None):
                    flags.append("missing_meta")

                updated = getattr(page, "updated_at", None)
                if updated and updated < stale_threshold:
                    flags.append("stale")

                items.append({
                    "id": page.pk,
                    "source": "seo_pages",
                    "type": "seo",
                    "title": page.title,
                    "slug": page.slug,
                    "edit_url": f"/admin/seo-pages/seo-pages/{page.pk}/change/",
                    "flags": flags,
                    "is_healthy": len(flags) == 0,
                })
                self._tally(summary, flags)

        except ImportError:
            pass

        # Sort: unhealthy first, then by title
        items.sort(key=lambda x: (len(x["flags"]) == 0, x["title"]))

        return Response({"summary": summary, "items": items})

    # ── helpers ──────────────────────────────────────────────────────────

    def _item(self, page, content_type: str, flags: list) -> dict:
        edit_url = f"/cms-admin/pages/{page.pk}/edit/"
        return {
            "id": page.pk,
            "source": "wagtail",
            "type": content_type,
            "title": page.title,
            "slug": page.slug,
            "edit_url": edit_url,
            "flags": flags,
            "is_healthy": len(flags) == 0,
        }

    def _tally(self, summary: dict, flags: list) -> None:
        summary["total"] += 1
        if flags:
            for f in flags:
                summary[f] = summary.get(f, 0) + 1
        else:
            summary["healthy"] += 1


# ---------------------------------------------------------------------------
# Wagtail draft creation — staff app → Wagtail handoff
# ---------------------------------------------------------------------------

class CreatePageDraftView(APIView):
    """
    POST /cms-api/pages/create-draft/

    Creates a Wagtail page as a draft under the correct index page for the
    current site, pre-filled with the fields the staff member entered in the
    publishing desk. Returns the Wagtail admin edit URL so the frontend can
    redirect staff directly to the rich editor.

    Body:
        {
          "type": "blog" | "service",
          "title": "How to write a nursing essay",
          "slug": "how-to-write-nursing-essay",
          "meta_description": "...",
          "primary_keyword": "nursing essay" (optional)
        }

    Response:
        { "page_id": 42, "edit_url": "/cms-admin/pages/42/edit/" }
    """

    permission_classes = [permissions.IsAuthenticated]

    STAFF_ROLES = ("superadmin", "admin", "editor")

    def post(self, request):
        user = request.user
        if getattr(user, "role", None) not in self.STAFF_ROLES and not user.is_staff:
            return Response(
                {"detail": "Only staff may create CMS drafts."},
                status=403,
            )

        page_type = request.data.get("type", "blog")
        title = (request.data.get("title") or "").strip()
        slug = (request.data.get("slug") or "").strip()
        meta_desc = request.data.get("meta_description", "")
        primary_kw = request.data.get("primary_keyword", "")

        if not title or not slug:
            return Response({"detail": "title and slug are required."}, status=400)

        # Prefer an explicit website_id from the request body so staff can
        # choose which tenant site they're publishing to.
        website_id = request.data.get("website_id")
        site = None

        if website_id:
            try:
                from websites.models.websites import Website
                from cms_core.services.tenant_service import get_site_for_website
                website = Website.objects.get(pk=website_id, is_active=True)
                site = get_site_for_website(website)
            except Exception:
                return Response(
                    {"detail": f"Website #{website_id} not found or has no linked Wagtail site."},
                    status=400,
                )

        # Fall back to the middleware-resolved site (single-site or client domain)
        if site is None:
            site = getattr(request, "site", None)

        # Last resort: default site
        if site is None:
            try:
                from wagtail.models import Site as WagtailSite
                site = WagtailSite.objects.filter(is_default_site=True).first()
            except Exception:
                pass

        if site is None:
            return Response(
                {"detail": "Could not resolve a Wagtail site. Pass website_id or access from a known domain."},
                status=400,
            )

        try:
            page_id, edit_url = self._create_draft(
                page_type, title, slug, meta_desc, primary_kw, site, user
            )
        except LookupError as exc:
            return Response({"detail": str(exc)}, status=400)
        except Exception as exc:
            return Response({"detail": f"Could not create draft: {exc}"}, status=500)

        return Response({"page_id": page_id, "edit_url": edit_url})

    def _create_draft(self, page_type, title, slug, meta_desc, primary_kw, site, user):
        from wagtail.models import Page

        if page_type == "blog":
            from cms_blog.models import BlogIndexPage, BlogPostPage

            index = (
                BlogIndexPage.objects.live()
                .descendant_of(site.root_page)
                .first()
            )
            if index is None:
                raise LookupError(
                    "No BlogIndexPage found under this site. "
                    "Run setup_tenants or create one in Wagtail first."
                )

            page = BlogPostPage(
                title=title,
                slug=slug,
                search_description=meta_desc,
                primary_author=None,
            )
            index.add_child(instance=page)

        elif page_type == "service":
            from cms_service_pages.models import ServiceIndexPage, ServicePage

            index = (
                ServiceIndexPage.objects.live()
                .descendant_of(site.root_page)
                .first()
            )
            if index is None:
                raise LookupError(
                    "No ServiceIndexPage found under this site. "
                    "Run setup_tenants or create one in Wagtail first."
                )

            page = ServicePage(
                title=title,
                slug=slug,
                search_description=meta_desc,
            )
            index.add_child(instance=page)

        else:
            raise LookupError(f"Unknown page type: {page_type!r}")

        # Save an initial revision so the page appears in the Wagtail edit UI
        # add_child() already sets live=False, so this is a proper draft.
        page.save_revision(user=user)

        edit_url = f"/cms-admin/pages/{page.id}/edit/"
        return page.id, edit_url


class PublicSiteSettingsView(APIView):
    """GET /cms-api/site-settings/
    Returns branding and SEO settings for the current site (tenant-scoped).
    Used by marketing frontends to apply favicon, OG image, GA4, and Schema.org.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from cms_core.models import TenantSEOSettings
        from cms_core.services.tenant_service import get_current_site

        site = get_current_site(request)
        if not site:
            return Response({})

        try:
            settings = TenantSEOSettings.for_site(site)
        except Exception:
            return Response({})

        def image_url(image, spec="original"):
            if not image:
                return None
            try:
                return image.get_rendition(spec).url
            except Exception:
                return getattr(getattr(image, "file", None), "url", None)

        return Response({
            "site_name": settings.site_name or site.site_name or "",
            "favicon_url": image_url(settings.favicon, "max-512x512"),
            "og_image_url": image_url(settings.default_og_image, "width-1200"),
            "schema_org_logo_url": image_url(settings.schema_org_logo, "max-512x512"),
            "google_analytics_id": settings.google_analytics_id or "",
            "schema_org_name": settings.schema_org_name or site.site_name or "",
        })


class PublicContactView(APIView):
    """POST /cms-api/contact/
    Accepts a contact enquiry from any marketing site.
    No authentication required.
    Tries email notification; always returns 201 so the form never fails visibly.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        name = (request.data.get("name") or "").strip()
        email = (request.data.get("email") or "").strip()
        subject = (request.data.get("subject") or "General enquiry").strip()
        message = (request.data.get("message") or "").strip()

        if not name or not email or not message:
            return Response(
                {"error": "name, email, and message are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        import logging
        logger = logging.getLogger("cms_core.contact")

        body = f"Name: {name}\nEmail: {email}\nSubject: {subject}\n\n{message}"
        logger.info("Contact enquiry received from %s <%s>: %s", name, email, subject)

        try:
            from django.core.mail import mail_managers
            mail_managers(f"[Contact] {subject}", body, fail_silently=True)
        except Exception:
            pass

        return Response({"ok": True}, status=status.HTTP_201_CREATED)