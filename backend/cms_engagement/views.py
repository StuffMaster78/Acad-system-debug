"""
Engagement API Views
======================

Public endpoints for the engagement bar on the public site:
- Get engagement summary for a page
- Post a reaction (toggle)
- Track a page view (JS beacon endpoint)
- Track a share
- Bookmark (authenticated only)

ID resolution
─────────────
All write endpoints accept two formats so that different marketing
frontends can call them without needing a content-type lookup:

  GradeCrest format  { content_type_id, object_id }
  NMG/EM/RPM format  { page_id }   ← Wagtail page PK, resolved here

Reaction types
──────────────
Canonical (stored):  thumbs_up | thumbs_down | love | useful
NMG/EM/RPM aliases:  helpful → thumbs_up | insightful → useful
"""

from django.contrib.contenttypes.models import ContentType
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from wagtail.models import Site as WagtailSite

from cms_engagement.models import (
    EngagementSummary,
    PageBookmark,
    PageReaction,
    PageShare,
    PageView,
)
from cms_engagement.serializers import EngagementSummarySerializer


# ── Helpers ───────────────────────────────────────────────────────────────────

def _resolve_site(request):
    """Return request.site; fall back to the default Wagtail site.

    Wagtail's SiteMiddleware maps the Host header to a site.  When the
    frontend calls from a different origin (e.g. :3000 → :8000), the
    header may not match and request.site is None.
    """
    site = getattr(request, "site", None)
    if site is None:
        site = (
            WagtailSite.objects.filter(is_default_site=True).first()
            or WagtailSite.objects.first()
        )
    return site


def _session_key(request) -> str:
    """Return a stable anonymous session key, creating one when needed."""
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key or ""


def _resolve_ids(data: dict) -> tuple[int | None, int | None]:
    """Resolve (content_type_id, object_id) from a request data dict.

    Accepts:
      { content_type_id, object_id }   — GradeCrest / direct format
      { page_id }                       — Wagtail page PK shortcut
    """
    ct_id  = data.get("content_type_id")
    obj_id = data.get("object_id")
    if ct_id and obj_id:
        return int(ct_id), int(obj_id)

    page_id = data.get("page_id")
    if page_id:
        try:
            from wagtail.models import Page
            page = Page.objects.get(pk=int(page_id)).specific
            ct = ContentType.objects.get_for_model(page.__class__)
            return ct.pk, page.pk
        except Exception:
            pass

    return None, None


# Canonical stored values; aliases let NMG/EM/RPM send friendlier names.
_REACTION_ALIASES: dict[str, str] = {
    "helpful":    "thumbs_up",
    "insightful": "useful",
}
_VALID_REACTIONS = {"thumbs_up", "thumbs_down", "love", "useful"}


def _canonical_reaction(raw: str) -> str:
    return _REACTION_ALIASES.get(raw, raw)


def _composable_stats(data: dict) -> dict:
    """Add composable-friendly aliases to a serializer response dict.

    The NMG / EM / RPM useEngagement composable reads:
      stats.views        → total_views
      stats.shares       → total_shares
      stats.reactions    → [{type, count}, …]  (using composable type names)
    """
    data["views"]  = data.get("total_views", 0)
    data["shares"] = data.get("total_shares", 0)
    data["reactions"] = [
        {"type": "helpful",    "count": data.get("thumbs_up_count",   0)},
        {"type": "love",       "count": data.get("love_count",         0)},
        {"type": "insightful", "count": data.get("useful_count",       0)},
    ]
    return data


# ── Views ─────────────────────────────────────────────────────────────────────

class PageEngagementView(APIView):
    """
    GET /cms-api/engagement/page/<content_type_id>/<object_id>/
    GET /cms-api/engagement/page/?page_id=<wagtail_page_id>

    Returns engagement summary. The ?page_id shortcut resolves the
    content_type automatically.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, content_type_id=None, object_id=None):
        if content_type_id is None:
            page_id = request.query_params.get("page_id")
            if not page_id:
                return Response(
                    {"error": "Provide path params or ?page_id"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ct_id, obj_id = _resolve_ids({"page_id": page_id})
            if not ct_id:
                return Response({"error": "Page not found"}, status=status.HTTP_404_NOT_FOUND)
            content_type_id, object_id = ct_id, obj_id

        try:
            summary = EngagementSummary.objects.get(
                content_type_id=content_type_id,
                object_id=object_id,
            )
            data = dict(EngagementSummarySerializer(summary).data)

            if request.user.is_authenticated:
                user_reaction = PageReaction.objects.filter(
                    content_type_id=content_type_id,
                    object_id=object_id,
                    user=request.user,
                ).values_list("reaction_type", flat=True).first()
                data["user_reaction"] = user_reaction

                data["user_bookmarked"] = PageBookmark.objects.filter(
                    content_type_id=content_type_id,
                    object_id=object_id,
                    user=request.user,
                ).exists()

            return Response(_composable_stats(data))

        except EngagementSummary.DoesNotExist:
            return Response(_composable_stats({
                "total_views": 0, "unique_views": 0,
                "thumbs_up_count": 0, "thumbs_down_count": 0,
                "love_count": 0, "useful_count": 0,
                "total_shares": 0, "engagement_score": 0,
            }))


class TrackPageView(APIView):
    """POST /cms-api/engagement/track-view/

    Body (either format):
      { content_type_id, object_id, time_on_page?, scroll_depth? }
      { page_id, time_on_page?, scroll_depth? }
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ct_id, obj_id = _resolve_ids(request.data)
        if not ct_id or not obj_id:
            return Response(
                {"error": "Provide content_type_id+object_id or page_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        site       = _resolve_site(request)
        session_id = _session_key(request)
        time_on_page = request.data.get("time_on_page", 0)
        scroll_depth = request.data.get("scroll_depth", 0)

        existing = PageView.objects.filter(
            content_type_id=ct_id,
            object_id=obj_id,
            session_id=session_id,
        ).order_by("-created_at").first()

        if existing:
            if time_on_page:
                existing.time_on_page = max(existing.time_on_page, int(time_on_page))
            if scroll_depth:
                existing.scroll_depth = max(existing.scroll_depth, int(scroll_depth))
            existing.save(update_fields=["time_on_page", "scroll_depth"])
        else:
            PageView.objects.create(
                content_type_id=ct_id,
                object_id=obj_id,
                site=site,
                session_id=session_id,
                user=request.user if request.user.is_authenticated else None,
                referrer=request.META.get("HTTP_REFERER", "")[:500],
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
                time_on_page=int(time_on_page or 0),
                scroll_depth=int(scroll_depth or 0),
            )

        return Response({"status": "ok"}, status=status.HTTP_201_CREATED)


class ReactToPage(APIView):
    """POST /cms-api/engagement/react/
    Toggle a reaction on a page.

    Body (either format):
      { content_type_id, object_id, reaction_type }
      { page_id, reaction_type }
      { page_id, reaction }          ← NMG/EM/RPM composable alias
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ct_id, obj_id = _resolve_ids(request.data)
        if not ct_id or not obj_id:
            return Response(
                {"error": "Provide content_type_id+object_id or page_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw_type = request.data.get("reaction_type") or request.data.get("reaction", "")
        reaction_type = _canonical_reaction(str(raw_type))
        if reaction_type not in _VALID_REACTIONS:
            return Response(
                {"error": f"reaction_type must be one of: {sorted(_VALID_REACTIONS)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        site = _resolve_site(request)

        lookup: dict = {"content_type_id": ct_id, "object_id": obj_id}
        if request.user.is_authenticated:
            lookup["user"] = request.user
        else:
            lookup["session_id"] = _session_key(request)

        existing = PageReaction.objects.filter(**lookup).first()

        if existing:
            if existing.reaction_type == reaction_type:
                existing.delete()
                return Response({"status": "removed", "reaction_type": None})
            existing.reaction_type = reaction_type
            existing.save(update_fields=["reaction_type"])
            return Response({"status": "changed", "reaction_type": reaction_type})

        PageReaction.objects.create(
            content_type_id=ct_id,
            object_id=obj_id,
            site=site,
            user=request.user if request.user.is_authenticated else None,
            session_id="" if request.user.is_authenticated else _session_key(request),
            reaction_type=reaction_type,
        )
        return Response(
            {"status": "added", "reaction_type": reaction_type},
            status=status.HTTP_201_CREATED,
        )


class SharePage(APIView):
    """POST /cms-api/engagement/share/

    Body (either format):
      { content_type_id, object_id, platform }
      { page_id, platform }
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ct_id, obj_id = _resolve_ids(request.data)
        platform = request.data.get("platform")

        if not ct_id or not obj_id or not platform:
            return Response(
                {"error": "Provide (content_type_id+object_id or page_id) and platform"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        site = _resolve_site(request)

        PageShare.objects.create(
            content_type_id=ct_id,
            object_id=obj_id,
            site=site,
            platform=platform,
            user=request.user if request.user.is_authenticated else None,
            session_id=request.session.session_key or "",
        )

        return Response({"status": "tracked"}, status=status.HTTP_201_CREATED)


class BookmarkPage(APIView):
    """POST /cms-api/engagement/bookmark/ — toggle (authenticated only).

    Body (either format):
      { content_type_id, object_id }
      { page_id }
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ct_id, obj_id = _resolve_ids(request.data)
        if not ct_id or not obj_id:
            return Response(
                {"error": "Provide content_type_id+object_id or page_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing = PageBookmark.objects.filter(
            content_type_id=ct_id,
            object_id=obj_id,
            user=request.user,
        ).first()

        if existing:
            existing.delete()
            return Response({"status": "removed", "bookmarked": False})

        PageBookmark.objects.create(
            content_type_id=ct_id,
            object_id=obj_id,
            user=request.user,
        )
        return Response(
            {"status": "added", "bookmarked": True},
            status=status.HTTP_201_CREATED,
        )

    def get(self, request):
        """GET /cms-api/engagement/bookmark/ — list user's bookmarks."""
        bookmarks = PageBookmark.objects.filter(
            user=request.user
        ).order_by("-created_at")[:50]

        data = []
        for b in bookmarks:
            try:
                obj = b.content_object
                data.append({
                    "content_type_id": b.content_type_id,
                    "object_id": b.object_id,
                    "title": getattr(obj, "title", str(obj)),
                    "url": getattr(obj, "url", ""),
                    "bookmarked_at": b.created_at,
                })
            except Exception:
                continue

        return Response(data)
