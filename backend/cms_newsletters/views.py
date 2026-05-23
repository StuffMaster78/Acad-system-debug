from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from cms_newsletters.serializers import SubscribeSerializer, UnsubscribeSerializer


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
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        site = getattr(request, "site", None)
        if not site:
            return Response({"error": "No site context"}, status=400)

        from cms_newsletters.services.subscriber_service import SubscriberService

        return Response(SubscriberService.get_stats(site))
