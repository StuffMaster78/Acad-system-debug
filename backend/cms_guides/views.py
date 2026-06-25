from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from wagtail.models import Site

from .models import GuideArticlePage, GuideAudience


def _get_site(request):
    """Resolve the Wagtail site from the request host."""
    try:
        return Site.find_for_request(request)
    except Exception:
        return None


def _audience_filter(role: str) -> list[str]:
    """
    Return the list of audience values that should be visible for a given
    portal role.  Staff & admin roles see both 'all' and 'staff' guides.
    """
    role = (role or "").lower()
    if role in ("superadmin", "admin", "editor", "support", "staff"):
        return [GuideAudience.ALL, GuideAudience.STAFF]
    if role == "writer":
        return [GuideAudience.ALL, GuideAudience.WRITER]
    if role == "client":
        return [GuideAudience.ALL, GuideAudience.CLIENT]
    return [GuideAudience.ALL]


def _serialise_article(page: GuideArticlePage, detail: bool = False) -> dict:
    pdf = page.pdf_attachment
    data: dict = {
        "id":                      page.pk,
        "slug":                    page.slug,
        "title":                   page.title,
        "summary":                 page.summary,
        "audience":                page.audience,
        "icon":                    page.icon or "book-open",
        "is_featured":             page.is_featured,
        "estimated_read_minutes":  page.estimated_read_minutes,
        "published_at":            (
            page.last_published_at.isoformat() if page.last_published_at else None
        ),
        "pdf": {"title": pdf.title, "url": pdf.url} if pdf else None,
    }
    if detail:
        data["body"] = page.body  # HTML string from RichTextField
    return data


class GuideListView(APIView):
    """
    GET /cms-api/guides/
    Returns published guides visible to the requesting user's role.
    Query params:
      ?audience=staff   (optional — if omitted, defaults based on user role)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = getattr(request.user, "role", "") or ""
        audience_filter = _audience_filter(role)

        site = _get_site(request)
        qs = GuideArticlePage.objects.live().public().filter(
            audience__in=audience_filter,
        )
        if site:
            qs = qs.descendant_of(site.root_page)

        qs = qs.order_by("-is_featured", "title")

        return Response({
            "items": [_serialise_article(p) for p in qs],
        })


class GuideDetailView(APIView):
    """
    GET /cms-api/guides/<slug>/
    Returns a single published guide including the full body HTML.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, slug: str):
        role = getattr(request.user, "role", "") or ""
        audience_filter = _audience_filter(role)

        site = _get_site(request)
        qs = GuideArticlePage.objects.live().public().filter(
            slug=slug,
            audience__in=audience_filter,
        )
        if site:
            qs = qs.descendant_of(site.root_page)

        page = qs.first()
        if page is None:
            return Response({"detail": "Not found."}, status=404)

        return Response(_serialise_article(page, detail=True))
