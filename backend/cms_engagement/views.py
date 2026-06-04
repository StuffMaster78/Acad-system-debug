"""
Engagement API Views
======================

Public endpoints for the engagement bar on the public site:
- Get engagement summary for a page
- Post a reaction (toggle)
- Track a page view (JS beacon endpoint)
- Track a share
- Bookmark (authenticated only)
"""

from django.contrib.contenttypes.models import ContentType
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from cms_engagement.models import (
    EngagementSummary,
    PageBookmark,
    PageReaction,
    PageShare,
    PageView,
)
from cms_engagement.serializers import EngagementSummarySerializer


class PageEngagementView(APIView):
    """
    GET /cms-api/engagement/page/<content_type_id>/<object_id>/
    GET /cms-api/engagement/page/?page_id=<wagtail_page_id>

    Returns engagement summary. The ?page_id shortcut resolves the content_type automatically.
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
            try:
                from wagtail.models import Page
                from django.contrib.contenttypes.models import ContentType as CT
                page = Page.objects.get(pk=int(page_id)).specific
                content_type_id = CT.objects.get_for_model(page).id
                object_id = page.pk
            except Exception:
                return Response({"error": "Page not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            summary = EngagementSummary.objects.get(
                content_type_id=content_type_id,
                object_id=object_id,
            )
            data = EngagementSummarySerializer(summary).data

            # Add user's own reaction if authenticated
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

            return Response(data)

        except EngagementSummary.DoesNotExist:
            return Response({
                "total_views": 0, "unique_views": 0,
                "thumbs_up_count": 0, "thumbs_down_count": 0,
                "love_count": 0, "useful_count": 0,
                "total_shares": 0, "engagement_score": 0,
            })


class TrackPageView(APIView):
    """POST /cms-api/engagement/track-view/
    Called by JS beacon on page load.

    Body: {
        "content_type_id": 42,
        "object_id": 123,
        "time_on_page": 45, (optional, updated via beacon)
        "scroll_depth": 72 (optional, updated via beacon)
    }
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ct_id = request.data.get("content_type_id")
        obj_id = request.data.get("object_id")

        if not ct_id or not obj_id:
            return Response(
                {"error": "content_type_id and object_id required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        site = getattr(request, "site", None)
        session_id = request.session.session_key or ""

        # Update existing view in same session, or create new
        existing = PageView.objects.filter(
            content_type_id=ct_id,
            object_id=obj_id,
            session_id=session_id,
        ).order_by("-created_at").first()

        time_on_page = request.data.get("time_on_page", 0)
        scroll_depth = request.data.get("scroll_depth", 0)

        if existing:
            # Update engagement depth
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

    Body: {
        "content_type_id": 42,
        "object_id": 123,
        "reaction_type": "thumbs_up"
    }
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ct_id = request.data.get("content_type_id")
        obj_id = request.data.get("object_id")
        reaction_type = request.data.get("reaction_type")

        if not all([ct_id, obj_id, reaction_type]):
            return Response(
                {"error": "content_type_id, object_id, and reaction_type required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        valid_types = ["thumbs_up", "thumbs_down", "love", "useful"]
        if reaction_type not in valid_types:
            return Response(
                {"error": f"reaction_type must be one of: {valid_types}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        site = getattr(request, "site", None)

        # Find existing reaction by user or session
        lookup = {
            "content_type_id": ct_id,
            "object_id": obj_id,
        }
        if request.user.is_authenticated:
            lookup["user"] = request.user
        else:
            lookup["session_id"] = request.session.session_key or ""

        existing = PageReaction.objects.filter(**lookup).first()

        if existing:
            if existing.reaction_type == reaction_type:
                # Toggle off
                existing.delete()
                return Response({"status": "removed", "reaction_type": None})
            else:
                # Change reaction
                existing.reaction_type = reaction_type
                existing.save(update_fields=["reaction_type"])
                return Response({"status": "changed", "reaction_type": reaction_type})
        else:
            PageReaction.objects.create(
                content_type_id=ct_id,
                object_id=obj_id,
                site=site,
                user=request.user if request.user.is_authenticated else None,
                session_id=request.session.session_key or "",
                reaction_type=reaction_type,
            )
            return Response(
                {"status": "added", "reaction_type": reaction_type},
                status=status.HTTP_201_CREATED,
            )


class SharePage(APIView):
    """POST /cms-api/engagement/share/
    Track a share-button click.

    Body: {
        "content_type_id": 42,
        "object_id": 123,
        "platform": "twitter"
    }
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ct_id = request.data.get("content_type_id")
        obj_id = request.data.get("object_id")
        platform = request.data.get("platform")

        if not all([ct_id, obj_id, platform]):
            return Response(
                {"error": "content_type_id, object_id, and platform required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        site = getattr(request, "site", None)

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
    """POST /cms-api/engagement/bookmark/
    Toggle bookmark (authenticated only).

    Body: {"content_type_id": 42, "object_id": 123}
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ct_id = request.data.get("content_type_id")
        obj_id = request.data.get("object_id")

        if not all([ct_id, obj_id]):
            return Response(
                {"error": "content_type_id and object_id required"},
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