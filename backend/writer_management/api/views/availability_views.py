from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
 
from writer_management.api.permissions import (
    IsAdminUser, IsWriterUser, IsAdminOrWriterOwner,
    _resolve_website,
)
from writer_management.utils import get_writer_profile_for_website
from writer_management.services.availability_service import AvailabilityService
from writer_management.models.writer_availability import WriterAvailabilityWindow
 
 
class MyAvailabilityView(APIView):
    """
    GET  /api/writer-management/me/availability/
    POST /api/writer-management/me/availability/declare/
    """
    permission_classes = [IsWriterUser]
 
    def get(self, request):
        website = _resolve_website(request)
        profile = get_writer_profile_for_website(request.user, website)
        active = AvailabilityService.get_active_window(profile)
        upcoming = list(AvailabilityService.get_upcoming_windows(profile))
 
        from writer_management.api.serializers.misc_serializers import (
            WriterAvailabilityWindowSerializer,
        )
        return Response({
            "active_window": (
                WriterAvailabilityWindowSerializer(active).data
                if active else None
            ),
            "upcoming_windows": WriterAvailabilityWindowSerializer(
                upcoming, many=True
            ).data,
        })
 
 
class DeclareUnavailableView(APIView):
    """POST /api/writer-management/me/availability/declare/"""
    permission_classes = [IsWriterUser]
 
    def post(self, request):
        from writer_management.api.serializers.misc_serializers import (
            DeclareUnavailableSerializer,
            WriterAvailabilityWindowSerializer,
        )
        website = _resolve_website(request)
        profile = get_writer_profile_for_website(request.user, website)
 
        serializer = DeclareUnavailableSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
 
        window = AvailabilityService.declare_unavailable(
            writer_profile=profile,
            start_at=d["start_at"],
            end_at=d.get("end_at"),
            reason=d["reason"],
            note=d.get("note", ""),
        )
        return Response(
            WriterAvailabilityWindowSerializer(window).data,
            status=status.HTTP_201_CREATED,
        )
 
 
class EndAvailabilityWindowView(APIView):
    """POST /api/writer-management/me/availability/<pk>/end/"""
    permission_classes = [IsWriterUser]
 
    def post(self, request, pk):
        website = _resolve_website(request)
        profile = get_writer_profile_for_website(request.user, website)
 
        try:
            window = WriterAvailabilityWindow.objects.get(
                pk=pk, writer=profile
            )
        except WriterAvailabilityWindow.DoesNotExist:
            return Response({"detail": "Window not found."}, status=404)
 
        AvailabilityService.end_window(window)
        return Response({"detail": "Availability window ended."})
 
 
class ToggleAcceptingOrdersView(APIView):
    """POST /api/writer-management/me/availability/toggle/"""
    permission_classes = [IsWriterUser]
 
    def post(self, request):
        website = _resolve_website(request)
        profile = get_writer_profile_for_website(request.user, website)
        accepting = request.data.get("is_accepting_orders")
        if accepting is None:
            return Response(
                {"detail": "is_accepting_orders is required."},
                status=400,
            )
        AvailabilityService.set_accepting_orders(
            writer_profile=profile,
            accepting=bool(accepting),
        )
        return Response({
            "detail": "Updated.",
            "is_accepting_orders": bool(accepting),
        })
 
 
class UpdateAvailabilityPreferencesView(APIView):
    """PATCH /api/writer-management/me/availability/preferences/"""
    permission_classes = [IsWriterUser]
 
    def patch(self, request):
        from writer_management.api.serializers.availability_serializers import (
            WriterAvailabilityPreferenceSerializer,
        )
        website = _resolve_website(request)
        profile = get_writer_profile_for_website(request.user, website)
 
        serializer = WriterAvailabilityPreferenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
 
        pref = AvailabilityService.update_preferences(
            writer_profile=profile,
            **serializer.validated_data,
        )
        return Response(
            WriterAvailabilityPreferenceSerializer(pref).data
        )