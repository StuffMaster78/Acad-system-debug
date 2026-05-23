"""
CMS Core Views
================

API endpoints for content import/paste functionality.
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
            "format": "html"   // or "text"
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