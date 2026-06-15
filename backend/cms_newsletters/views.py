from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.permissions import IsAdminOrSuperAdmin

from cms_newsletters.serializers import (
    SubscribeSerializer,
    UnsubscribeSerializer,
    SubscriberListSerializer,
    NewsletterListSerializer,
    NewsletterDetailSerializer,
    SubscriberCategorySerializer,
)


class SubscribeView(APIView):
    """POST /cms-api/newsletters/subscribe/"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        site = getattr(request, "site", None)
        if not site:
            return Response({"error": "No site context"}, status=400)

        from cms_newsletters.services.subscriber_service import SubscriberService

        result = SubscriberService.subscribe(
            site=site,
            email=serializer.validated_data["email"],
            source=serializer.validated_data.get("source", "blog_form"),
            source_detail=serializer.validated_data.get("source_detail", ""),
            consent_marketing=serializer.validated_data.get("consent_marketing", False),
            frequency=serializer.validated_data.get("frequency", "weekly"),
        )
        return Response(result, status=status.HTTP_201_CREATED)


class UnsubscribeView(APIView):
    """POST /cms-api/newsletters/unsubscribe/"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UnsubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        site = getattr(request, "site", None)
        if not site:
            return Response({"error": "No site context"}, status=400)

        from cms_newsletters.services.subscriber_service import SubscriberService

        success = SubscriberService.unsubscribe(
            site=site,
            email=serializer.validated_data["email"],
            reason=serializer.validated_data.get("reason", "other"),
        )

        if success:
            return Response({"status": "unsubscribed"})
        return Response(
            {"error": "Email not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


class SubscriberStatsView(APIView):
    """GET /cms-api/newsletters/stats/ — admin only."""
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        site = getattr(request, "site", None)
        if not site:
            return Response({"error": "No site context"}, status=400)

        from cms_newsletters.services.subscriber_service import SubscriberService

        return Response(SubscriberService.get_stats(site))


# ── Admin views ──────────────────────────────────────────────────────────────

class AdminSubscriberListView(APIView):
    """GET /cms-api/newsletters/admin/subscribers/"""
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        from cms_newsletters.models import Subscriber

        site = getattr(request, "site", None)
        if not site:
            return Response({"error": "No site context"}, status=400)

        qs = Subscriber.objects.filter(site=site).prefetch_related("categories")

        # Filters
        is_active = request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == "true")

        source = request.query_params.get("source")
        if source:
            qs = qs.filter(source=source)

        frequency = request.query_params.get("frequency")
        if frequency:
            qs = qs.filter(frequency=frequency)

        search = request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(email__icontains=search)

        qs = qs.order_by("-created_at")

        # Simple pagination
        page_size = int(request.query_params.get("page_size", 50))
        page = int(request.query_params.get("page", 1))
        offset = (page - 1) * page_size
        total = qs.count()
        items = qs[offset: offset + page_size]

        return Response({
            "count": total,
            "page": page,
            "page_size": page_size,
            "results": SubscriberListSerializer(items, many=True).data,
        })


class AdminSubscriberActionView(APIView):
    """POST /cms-api/newsletters/admin/subscribers/<pk>/deactivate|reactivate/"""
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, pk, action):
        from cms_newsletters.models import Subscriber
        from django.utils import timezone

        try:
            subscriber = Subscriber.objects.get(pk=pk)
        except Subscriber.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)

        if action == "deactivate":
            subscriber.is_active = False
            subscriber.unsubscribed_at = timezone.now()
            subscriber.unsubscribe_reason = "other"
            subscriber.save(update_fields=["is_active", "unsubscribed_at", "unsubscribe_reason"])
            return Response({"detail": "Subscriber deactivated."})

        if action == "reactivate":
            subscriber.is_active = True
            subscriber.unsubscribed_at = None
            subscriber.unsubscribe_reason = ""
            subscriber.save(update_fields=["is_active", "unsubscribed_at", "unsubscribe_reason"])
            return Response({"detail": "Subscriber reactivated."})

        return Response({"detail": "Unknown action."}, status=400)


class AdminNewsletterListView(APIView):
    """GET /cms-api/newsletters/admin/newsletters/"""
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        from cms_newsletters.models import Newsletter

        site = getattr(request, "site", None)
        if not site:
            return Response({"error": "No site context"}, status=400)

        qs = Newsletter.objects.filter(site=site).select_related("analytics")

        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)

        search = request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(title__icontains=search)

        qs = qs.order_by("-created_at")

        page_size = int(request.query_params.get("page_size", 30))
        page = int(request.query_params.get("page", 1))
        offset = (page - 1) * page_size
        total = qs.count()
        items = qs[offset: offset + page_size]

        return Response({
            "count": total,
            "page": page,
            "page_size": page_size,
            "results": NewsletterListSerializer(items, many=True).data,
        })


class AdminNewsletterDetailView(APIView):
    """GET /cms-api/newsletters/admin/newsletters/<pk>/"""
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request, pk):
        from cms_newsletters.models import Newsletter

        try:
            newsletter = Newsletter.objects.select_related(
                "category", "analytics", "created_by"
            ).get(pk=pk)
        except Newsletter.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)

        return Response(NewsletterDetailSerializer(newsletter).data)


class AdminSubscriberCategoryListView(APIView):
    """GET  /cms-api/newsletters/admin/categories/
       POST /cms-api/newsletters/admin/categories/
    """
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        from cms_newsletters.models import SubscriberCategory

        site = getattr(request, "site", None)
        if not site:
            return Response({"error": "No site context"}, status=400)

        cats = SubscriberCategory.objects.filter(site=site).order_by("name")
        return Response(SubscriberCategorySerializer(cats, many=True).data)

    def post(self, request):
        from cms_newsletters.models import SubscriberCategory
        from django.utils.text import slugify

        site = getattr(request, "site", None)
        if not site:
            return Response({"error": "No site context"}, status=400)

        name = (request.data.get("name") or "").strip()
        if not name:
            return Response({"detail": "name is required."}, status=400)

        slug = slugify(name)
        cat, created = SubscriberCategory.objects.get_or_create(
            site=site, slug=slug, defaults={"name": name}
        )
        return Response(
            SubscriberCategorySerializer(cat).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
