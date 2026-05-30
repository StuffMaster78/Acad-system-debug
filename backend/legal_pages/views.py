from __future__ import annotations

from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .models import HelpArticle, HelpCategory, LegalDocument, UserAgreement


# ────────────────────────────────────────────────────────────────────────────
# Serializers (inline to keep the app self-contained)
# ────────────────────────────────────────────────────────────────────────────

class LegalDocumentSerializer(serializers.ModelSerializer):
    doc_type_display = serializers.CharField(source="get_doc_type_display", read_only=True)

    class Meta:
        model = LegalDocument
        fields = (
            "id", "doc_type", "doc_type_display", "title",
            "content", "version", "effective_date",
            "requires_re_acceptance",
        )


class HelpCategorySerializer(serializers.ModelSerializer):
    article_count = serializers.SerializerMethodField()

    class Meta:
        model = HelpCategory
        fields = (
            "id", "title", "slug", "description",
            "icon", "audience", "order", "article_count",
        )

    def get_article_count(self, obj) -> int:
        return obj.articles.filter(is_published=True).count()


class HelpArticleListSerializer(serializers.ModelSerializer):
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    category_title = serializers.CharField(source="category.title", read_only=True)

    class Meta:
        model = HelpArticle
        fields = (
            "id", "title", "slug", "summary",
            "audience", "is_featured", "category_slug", "category_title",
            "updated_at",
        )


class HelpArticleDetailSerializer(serializers.ModelSerializer):
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    category_title = serializers.CharField(source="category.title", read_only=True)

    class Meta:
        model = HelpArticle
        fields = (
            "id", "title", "slug", "summary", "content",
            "audience", "is_featured", "category_slug", "category_title",
            "updated_at",
        )


# ────────────────────────────────────────────────────────────────────────────
# Legal document endpoints
# ────────────────────────────────────────────────────────────────────────────

@api_view(["GET"])
@permission_classes([AllowAny])
def legal_document(request: Request, doc_type: str) -> Response:
    """
    GET /api/v1/legal/<doc_type>/
    Return the active legal document for the tenant's website.
    """
    website = getattr(request, "website", None)
    if website is None:
        return Response({"detail": "Website context missing."}, status=400)

    doc = LegalDocument.objects.filter(
        website=website,
        doc_type=doc_type,
        is_active=True,
    ).first()

    if doc is None:
        return Response(
            {"detail": f"No active '{doc_type}' document found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(LegalDocumentSerializer(doc).data)


@api_view(["GET"])
@permission_classes([AllowAny])
def legal_document_list(request: Request) -> Response:
    """
    GET /api/v1/legal/
    Return all active document types and their basic metadata.
    """
    website = getattr(request, "website", None)
    if website is None:
        return Response({"detail": "Website context missing."}, status=400)

    docs = LegalDocument.objects.filter(
        website=website,
        is_active=True,
    ).order_by("doc_type")

    return Response(LegalDocumentSerializer(docs, many=True).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def record_agreement(request: Request, doc_type: str) -> Response:
    """
    POST /api/v1/legal/<doc_type>/agree/
    Record that the authenticated user has accepted the active document.
    """
    website = getattr(request, "website", None)
    if website is None:
        return Response({"detail": "Website context missing."}, status=400)

    doc = LegalDocument.objects.filter(
        website=website,
        doc_type=doc_type,
        is_active=True,
    ).first()

    if doc is None:
        return Response(
            {"detail": f"No active '{doc_type}' document."},
            status=status.HTTP_404_NOT_FOUND,
        )

    meta = request.META
    ip = (
        meta.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
        or meta.get("REMOTE_ADDR", "")
    )

    _, created = UserAgreement.objects.get_or_create(
        user=request.user,
        document=doc,
        defaults={
            "ip_address": ip or None,
            "user_agent": meta.get("HTTP_USER_AGENT", "")[:500],
        },
    )

    return Response(
        {"agreed": True, "doc_type": doc_type, "version": doc.version, "new": created},
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
    )


# ────────────────────────────────────────────────────────────────────────────
# Help center endpoints
# ────────────────────────────────────────────────────────────────────────────

@api_view(["GET"])
@permission_classes([AllowAny])
def help_categories(request: Request) -> Response:
    """
    GET /api/v1/help/categories/
    Return all active help categories visible to the requesting user.
    """
    website = getattr(request, "website", None)
    if website is None:
        return Response({"detail": "Website context missing."}, status=400)

    audience = _resolve_audience(request)

    qs = HelpCategory.objects.filter(
        website=website,
        is_active=True,
        audience__in=["all", audience],
    ).order_by("order", "title")

    return Response(HelpCategorySerializer(qs, many=True).data)


@api_view(["GET"])
@permission_classes([AllowAny])
def help_articles(request: Request) -> Response:
    """
    GET /api/v1/help/articles/
    Return published articles. Filterable by ?category=<slug>&featured=true.
    """
    website = getattr(request, "website", None)
    if website is None:
        return Response({"detail": "Website context missing."}, status=400)

    audience = _resolve_audience(request)

    qs = HelpArticle.objects.filter(
        website=website,
        is_published=True,
        audience__in=["all", audience],
    ).select_related("category").order_by("category__order", "order", "title")

    category_slug = request.query_params.get("category")
    if category_slug:
        qs = qs.filter(category__slug=category_slug)

    if request.query_params.get("featured") == "true":
        qs = qs.filter(is_featured=True)

    return Response(HelpArticleListSerializer(qs, many=True).data)


@api_view(["GET"])
@permission_classes([AllowAny])
def help_article_detail(request: Request, slug: str) -> Response:
    """
    GET /api/v1/help/articles/<slug>/
    Return the full content of a single published article.
    """
    website = getattr(request, "website", None)
    if website is None:
        return Response({"detail": "Website context missing."}, status=400)

    audience = _resolve_audience(request)

    try:
        article = HelpArticle.objects.select_related("category").get(
            website=website,
            slug=slug,
            is_published=True,
            audience__in=["all", audience],
        )
    except HelpArticle.DoesNotExist:
        return Response({"detail": "Article not found."}, status=status.HTTP_404_NOT_FOUND)

    return Response(HelpArticleDetailSerializer(article).data)


# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────

def _resolve_audience(request: Request) -> str:
    """
    Return the audience key for the requesting user.
    Unauthenticated → "all" only.
    """
    user = request.user
    if not getattr(user, "is_authenticated", False):
        return "all"
    role = getattr(user, "role", "")
    if role in ("writer", "editor"):
        return "writer"
    if role in ("support", "admin", "superadmin"):
        return "staff"
    return "client"
