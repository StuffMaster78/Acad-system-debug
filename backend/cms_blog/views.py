"""
Blog post public API views.
"""

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from cms_blog.models import BlogPostPage


class BlogPostHistoryView(APIView):
    """
    GET /cms-api/blog/<page_id>/history/

    Returns the editorial timeline for a blog post:
    - first_published_at
    - last_substantive_update
    - revision_count (all Wagtail saves — quality signal)
    - structured updates list for frontend rendering
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, page_id: int):
        try:
            page = BlogPostPage.objects.get(pk=page_id, live=True)
        except BlogPostPage.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)

        revision_count = page.revisions.count()

        canonical_pub = page.canonical_published_at
        updates = []
        if canonical_pub:
            label = "First published"
            if page.original_published_at:
                label = "Originally published (migrated content)"
            updates.append({
                "date": canonical_pub.isoformat(),
                "type": "published",
                "label": label,
            })

        if (
            page.last_substantive_update
            and page.last_substantive_update != page.first_published_at
        ):
            updates.append({
                "date": page.last_substantive_update.isoformat(),
                "type": "updated",
                "label": "Content updated",
            })

        # Surface the last Wagtail save date as "last reviewed" if it's
        # more recent than last_substantive_update and at least 1 day newer
        # than the last item we already have.
        try:
            latest_revision = page.revisions.order_by("-created_at").first()
            if latest_revision:
                latest_dt = latest_revision.created_at
                threshold = (
                    page.last_substantive_update or page.first_published_at
                )
                if threshold and (latest_dt - threshold).days >= 1:
                    updates.append({
                        "date": latest_dt.isoformat(),
                        "type": "reviewed",
                        "label": "Reviewed & verified",
                    })
        except Exception:
            pass

        return Response({
            "first_published_at": page.first_published_at,
            "last_published_at": page.last_published_at,
            "last_substantive_update": page.last_substantive_update,
            "revision_count": revision_count,
            "updates": updates,
        })
