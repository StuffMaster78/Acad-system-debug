"""
Image Manager API
=================

Provides a simple REST interface for assigning featured images to
BlogPostPage and ServicePage objects — designed for the Vue portal's
Image Manager view used by non-technical editors.

Endpoints
---------
GET  /cms-api/image-manager/pages/
    Returns all blog posts and service pages with their image status.
    Optionally filter by ?site=hostname&type=blog|service&missing=1.

POST /cms-api/image-manager/pages/<page_id>/image/
    Upload a new image (multipart/form-data, field: "image") and assign it
    to the page. Returns the updated page record.

DELETE /cms-api/image-manager/pages/<page_id>/image/
    Removes the assigned image from the page.
"""

from __future__ import annotations

import io
from typing import Any

from django.core.files.base import ContentFile
from rest_framework import permissions, status
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from cms_blog.models import BlogPostPage
from cms_service_pages.models import ServicePage


# ── helpers ──────────────────────────────────────────────────────────────────

def _image_data(image) -> dict | None:
    if not image:
        return None
    try:
        thumb = image.get_rendition("fill-400x225|format-webp")
        full  = image.get_rendition("fill-1200x630|format-webp")
        return {
            "id":        image.id,
            "title":     image.title,
            "thumbnail": thumb.url,
            "full":      full.url,
            "width":     image.width,
            "height":    image.height,
        }
    except Exception:
        return {"id": image.id, "title": image.title, "thumbnail": None, "full": None}


def _page_record(page, kind: str) -> dict:
    img = page.featured_image if kind == "blog" else page.og_image
    try:
        site = page.get_site()
        hostname  = site.hostname if site else ""
        site_name = site.site_name if site else hostname
    except Exception:
        hostname = site_name = ""

    return {
        "id":       page.id,
        "type":     kind,
        "title":    page.title,
        "slug":     page.slug,
        "site":     hostname,
        "siteName": site_name,
        "editUrl":  f"/cms-admin/pages/{page.id}/edit/",
        "image":    _image_data(img),
    }


def _get_page(page_id: int):
    """Return (page, kind) for a given page id, searching both types."""
    try:
        return BlogPostPage.objects.get(pk=page_id), "blog"
    except BlogPostPage.DoesNotExist:
        pass
    try:
        return ServicePage.objects.get(pk=page_id), "service"
    except ServicePage.DoesNotExist:
        pass
    return None, None


def _assign_and_save(page, kind: str, image) -> None:
    if kind == "blog":
        page.featured_image = image
    else:
        page.og_image = image
    page.save_revision().publish()


def _upload_image(file, title: str):
    """Create a Wagtail image from an uploaded file object."""
    from wagtail.images import get_image_model
    Image = get_image_model()
    content = ContentFile(file.read())
    img = Image(title=title)
    img.file.save(file.name, content, save=True)
    return img


# ── views ────────────────────────────────────────────────────────────────────

class ImageManagerPageListView(APIView):
    """GET /cms-api/image-manager/pages/"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        site_filter    = request.query_params.get("site", "").strip()
        type_filter    = request.query_params.get("type", "").strip()    # blog | service
        missing_only   = request.query_params.get("missing") == "1"
        search         = request.query_params.get("q", "").strip()

        records: list[dict] = []

        # --- Blog posts ---
        if type_filter in ("", "blog"):
            qs = BlogPostPage.objects.live().order_by("title")
            if site_filter:
                from wagtail.models import Site
                try:
                    site = Site.objects.get(hostname=site_filter)
                    qs = qs.filter(path__startswith=site.root_page.path)
                except Site.DoesNotExist:
                    qs = qs.none()
            if missing_only:
                qs = qs.filter(featured_image__isnull=True)
            if search:
                qs = qs.filter(title__icontains=search)
            for page in qs.select_related("featured_image"):
                records.append(_page_record(page, "blog"))

        # --- Service pages ---
        if type_filter in ("", "service"):
            qs = ServicePage.objects.live().order_by("title")
            if site_filter:
                from wagtail.models import Site
                try:
                    site = Site.objects.get(hostname=site_filter)
                    qs = qs.filter(path__startswith=site.root_page.path)
                except Site.DoesNotExist:
                    qs = qs.none()
            if missing_only:
                qs = qs.filter(og_image__isnull=True)
            if search:
                qs = qs.filter(title__icontains=search)
            for page in qs.select_related("og_image"):
                records.append(_page_record(page, "service"))

        # Summary counts
        total   = len(records)
        missing = sum(1 for r in records if r["image"] is None)

        return Response({"results": records, "total": total, "missing": missing})


class ImageManagerPageImageView(APIView):
    """POST / DELETE /cms-api/image-manager/pages/<page_id>/image/"""

    permission_classes = [permissions.IsAuthenticated]
    parser_classes     = [MultiPartParser]

    def post(self, request: Request, page_id: int) -> Response:
        file = request.FILES.get("image")
        if not file:
            return Response({"error": "No image file provided."}, status=status.HTTP_400_BAD_REQUEST)

        allowed = {"image/jpeg", "image/png", "image/webp", "image/avif", "image/gif"}
        if file.content_type not in allowed:
            return Response(
                {"error": f"Unsupported file type: {file.content_type}. Use JPEG, PNG, or WebP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        page, kind = _get_page(page_id)
        if page is None:
            return Response({"error": "Page not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            title = file.name.rsplit(".", 1)[0].replace("-", " ").replace("_", " ").title()
            image = _upload_image(file, title)
            _assign_and_save(page, kind, image)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(_page_record(page, kind), status=status.HTTP_200_OK)

    def delete(self, request: Request, page_id: int) -> Response:
        page, kind = _get_page(page_id)
        if page is None or kind is None:
            return Response({"error": "Page not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            _assign_and_save(page, kind, None)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(_page_record(page, kind), status=status.HTTP_200_OK)
