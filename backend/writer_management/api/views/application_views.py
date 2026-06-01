from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from writer_management.api.serializers.application_serializers import (
    WriterApplicationSummarySerializer,
    WriterApplicationDetailSerializer,
    SubmitApplicationSerializer,
    ApproveApplicationSerializer,
    RejectApplicationSerializer,
)
from writer_management.services.writer_application_service import (
    WriterApplicationService,
)
from writer_management.models.writer_application import WriterApplication
from writer_management.api.filters.writer_filters import WriterApplicationFilter
from writer_management.api.permissions import IsAdminUser
from writer_management.api.permissions import _resolve_website


class WriterApplicationViewSet(ViewSet):
    """
    /api/writer-management/applications/

    list GET — admin: all applications with filters
    retrieve GET — admin: single application detail
    submit POST — public: submit new application
    review POST — admin: mark under review
    approve POST — admin: approve application
    reject POST — admin: reject application
    withdraw POST — applicant: withdraw own application
    """

    def get_permissions(self):
        if self.action in ("submit", "withdraw"):
            return [] # public or applicant
        return [IsAdminUser()]

    def list(self, request):
        from django_filters.rest_framework import DjangoFilterBackend
        website = _resolve_website(request)
        qs = WriterApplication.objects.filter(
            website=website
        ).select_related("reviewed_by").order_by("-submitted_at")

        filterset = WriterApplicationFilter(request.GET, queryset=qs)
        page = filterset.qs

        serializer = WriterApplicationSummarySerializer(page, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            application = WriterApplication.objects.get(pk=pk)
        except WriterApplication.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)
        return Response(
            WriterApplicationDetailSerializer(application).data
        )

    @action(detail=False, methods=["post"])
    def submit(self, request):
        website = _resolve_website(request)
        if website is None:
            return Response({"detail": "Website required."}, status=400)
        serializer = SubmitApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        try:
            application = WriterApplicationService.submit(
                website=website,
                **d,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response(
            WriterApplicationSummarySerializer(application).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        try:
            application = WriterApplication.objects.get(pk=pk)
        except WriterApplication.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)
        try:
            WriterApplicationService.mark_under_review(
                application=application,
                reviewed_by=request.user,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response({"detail": "Marked under review."})

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        try:
            application = WriterApplication.objects.get(pk=pk)
        except WriterApplication.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)
        serializer = ApproveApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        initial_level = None
        level_id = d.get("initial_level_id")
        if level_id:
            from writer_management.models.writer_level import WriterLevel
            try:
                initial_level = WriterLevel.objects.get(pk=level_id)
            except WriterLevel.DoesNotExist:
                return Response(
                    {"detail": f"WriterLevel {level_id} not found."},
                    status=400,
                )

        try:
            writer_profile = WriterApplicationService.approve(
                application=application,
                reviewed_by=request.user,
                initial_level=initial_level,
                require_review=d["require_review"],
            )
        except Exception as exc:
            return Response({"detail": str(exc)}, status=400)

        return Response({
            "detail": "Application approved.",
            "registration_id": writer_profile.registration_id,
            "public_uuid": str(writer_profile.public_uuid),
        })

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        try:
            application = WriterApplication.objects.get(pk=pk)
        except WriterApplication.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)
        serializer = RejectApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        try:
            WriterApplicationService.reject(
                application=application,
                reviewed_by=request.user,
                rejection_reason=d["rejection_reason"],
                admin_notes=d.get("admin_notes", ""),
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response({"detail": "Application rejected."})

    @action(detail=True, methods=["post"])
    def withdraw(self, request, pk=None):
        try:
            application = WriterApplication.objects.get(pk=pk)
        except WriterApplication.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)
        try:
            WriterApplicationService.withdraw(application=application)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response({"detail": "Application withdrawn."})
