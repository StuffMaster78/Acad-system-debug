from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from writer_management.api.permissions import IsAdminUser, IsAdminOrWriterOwner
from writer_management.api.filters.writer_filters import (
    WriterWarningFilter,
    WriterStrikeFilter,
)
from writer_management.api.serializers.discipline_serializers import (
    WriterWarningSerializer,
    IssueWarningSerializer,
    VoidWarningSerializer,
    WriterStrikeSerializer,
    IssueStrikeSerializer,
    VoidStrikeSerializer,
    WriterSuspensionSerializer,
    SuspendWriterSerializer,
    LiftSuspensionSerializer,
    WriterBlacklistSerializer,
    BlacklistWriterSerializer,
    LiftBlacklistSerializer,
    WriterProbationSerializer,
    PlaceProbationSerializer,
    WriterPenaltySerializer,
    ApplyPenaltySerializer,
    WriterDisciplineStateSerializer,
)
from writer_management.services.discipline_service import DisciplineService
from writer_management.services.writer_warning_service import WriterWarningService
from writer_management.services.writer_profile_service import WriterProfileService
from writer_management.models.writer_warning import WriterWarning
from writer_management.models.writer_strike import WriterStrike
from writer_management.models.writer_discipline import (
    WriterSuspension, WriterBlacklist, WriterProbation, WriterPenalty,
)


def _get_writer_or_404(registration_id):
    try:
        return WriterProfileService.get_by_registration_id(registration_id)
    except Exception:
        return None


# ----------------------------------------------------------------
# DISCIPLINE STATE
# ----------------------------------------------------------------

class WriterDisciplineStateView(APIView):
    """GET /api/writer-management/writers/<rid>/discipline/"""
    permission_classes = [IsAdminUser]

    def get(self, request, registration_id):
        writer = _get_writer_or_404(registration_id)
        if writer is None:
            return Response(
                {"detail": "Writer not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            state = writer.discipline_state
        except Exception:
            return Response(
                {"detail": "Discipline state not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(WriterDisciplineStateSerializer(state).data)


# ----------------------------------------------------------------
# WARNINGS
# ----------------------------------------------------------------

class WriterWarningListView(ListAPIView):
    """GET /api/writer-management/writers/<rid>/warnings/"""
    permission_classes = [IsAdminOrWriterOwner]
    serializer_class = WriterWarningSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = WriterWarningFilter

    def get_queryset(self):
        rid = self.kwargs["registration_id"]
        writer = _get_writer_or_404(rid)
        if writer is None:
            return WriterWarning.objects.none()
        return writer.warnings.select_related("issued_by").order_by("-created_at")


class IssueWarningView(APIView):
    """POST /api/writer-management/writers/<rid>/warnings/issue/"""
    permission_classes = [IsAdminUser]

    def post(self, request, registration_id):
        writer = _get_writer_or_404(registration_id)
        if writer is None:
            return Response({"detail": "Writer not found."}, status=404)
        serializer = IssueWarningSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        warning = WriterWarningService.issue_warning(
            writer=writer,
            reason=d["reason"],
            category=d["category"],
            issued_by=request.user,
            expires_days=d.get("expires_days"),
        )
        return Response(
            WriterWarningSerializer(warning).data,
            status=status.HTTP_201_CREATED,
        )


class VoidWarningView(APIView):
    """POST /api/writer-management/warnings/<pk>/void/"""
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            warning = WriterWarning.objects.get(pk=pk)
        except WriterWarning.DoesNotExist:
            return Response({"detail": "Warning not found."}, status=404)
        serializer = VoidWarningSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            WriterWarningService.void_warning(
                warning=warning,
                voided_by=request.user,
                reason=serializer.validated_data["reason"],
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response({"detail": "Warning voided."})


# ----------------------------------------------------------------
# STRIKES
# ----------------------------------------------------------------

class WriterStrikeListView(ListAPIView):
    """GET /api/writer-management/writers/<rid>/strikes/"""
    permission_classes = [IsAdminUser]
    serializer_class = WriterStrikeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = WriterStrikeFilter

    def get_queryset(self):
        rid = self.kwargs["registration_id"]
        writer = _get_writer_or_404(rid)
        if writer is None:
            return WriterStrike.objects.none()
        return writer.strikes.select_related("issued_by").order_by("-issued_at")


class IssueStrikeView(APIView):
    """POST /api/writer-management/writers/<rid>/strikes/issue/"""
    permission_classes = [IsAdminUser]

    def post(self, request, registration_id):
        writer = _get_writer_or_404(registration_id)
        if writer is None:
            return Response({"detail": "Writer not found."}, status=404)
        serializer = IssueStrikeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        strike = DisciplineService.issue_strike(
            writer=writer,
            reason=d["reason"],
            issued_by=request.user,
        )
        return Response(
            WriterStrikeSerializer(strike).data,
            status=status.HTTP_201_CREATED,
        )


class VoidStrikeView(APIView):
    """POST /api/writer-management/strikes/<pk>/void/"""
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            strike = WriterStrike.objects.get(pk=pk)
        except WriterStrike.DoesNotExist:
            return Response({"detail": "Strike not found."}, status=404)
        serializer = VoidStrikeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # DisciplineService.void_strike() — add when implemented
        strike.is_voided = True
        strike.void_reason = serializer.validated_data["reason"]
        strike.voided_by = request.user
        from django.utils.timezone import now
        strike.voided_at = now()
        strike.save(update_fields=[
            "is_voided", "void_reason", "voided_by", "voided_at"
        ])
        from writer_management.services.status_service import WriterStatusService
        WriterStatusService.recompute(strike.writer)
        return Response({"detail": "Strike voided."})


# ----------------------------------------------------------------
# SUSPENSION
# ----------------------------------------------------------------

class SuspendWriterView(APIView):
    """POST /api/writer-management/writers/<rid>/suspend/"""
    permission_classes = [IsAdminUser]

    def post(self, request, registration_id):
        writer = _get_writer_or_404(registration_id)
        if writer is None:
            return Response({"detail": "Writer not found."}, status=404)
        serializer = SuspendWriterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        try:
            suspension = DisciplineService.suspend(
                writer=writer,
                reason=d["reason"],
                duration_days=d.get("duration_days"),
                suspended_by=request.user,
            )
        except Exception as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response(
            WriterSuspensionSerializer(suspension).data,
            status=status.HTTP_201_CREATED,
        )


class LiftSuspensionView(APIView):
    """POST /api/writer-management/writers/<rid>/lift-suspension/"""
    permission_classes = [IsAdminUser]

    def post(self, request, registration_id):
        writer = _get_writer_or_404(registration_id)
        if writer is None:
            return Response({"detail": "Writer not found."}, status=404)
        serializer = LiftSuspensionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            DisciplineService.lift_suspension(
                writer=writer,
                lifted_by=request.user,
                reason=serializer.validated_data["reason"],
            )
        except Exception as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response({"detail": "Suspension lifted."})


# ----------------------------------------------------------------
# BLACKLIST
# ----------------------------------------------------------------

class BlacklistWriterView(APIView):
    """POST /api/writer-management/writers/<rid>/blacklist/"""
    permission_classes = [IsAdminUser]

    def post(self, request, registration_id):
        writer = _get_writer_or_404(registration_id)
        if writer is None:
            return Response({"detail": "Writer not found."}, status=404)
        serializer = BlacklistWriterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            entry = DisciplineService.blacklist(
                writer=writer,
                reason=serializer.validated_data["reason"],
                blacklisted_by=request.user,
            )
        except Exception as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response(
            WriterBlacklistSerializer(entry).data,
            status=status.HTTP_201_CREATED,
        )


class LiftBlacklistView(APIView):
    """POST /api/writer-management/writers/<rid>/lift-blacklist/"""
    permission_classes = [IsAdminUser]

    def post(self, request, registration_id):
        writer = _get_writer_or_404(registration_id)
        if writer is None:
            return Response({"detail": "Writer not found."}, status=404)
        serializer = LiftBlacklistSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            DisciplineService.lift_blacklist(
                writer=writer,
                lifted_by=request.user,
                reason=serializer.validated_data["reason"],
            )
        except Exception as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response({"detail": "Blacklist lifted."})


# ----------------------------------------------------------------
# PROBATION
# ----------------------------------------------------------------

class PlaceProbationView(APIView):
    """POST /api/writer-management/writers/<rid>/probation/"""
    permission_classes = [IsAdminUser]

    def post(self, request, registration_id):
        writer = _get_writer_or_404(registration_id)
        if writer is None:
            return Response({"detail": "Writer not found."}, status=404)
        serializer = PlaceProbationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        probation = DisciplineService.place_on_probation(
            writer=writer,
            reason=d["reason"],
            duration_days=d["duration_days"],
            placed_by=request.user,
        )
        return Response(
            WriterProbationSerializer(probation).data,
            status=status.HTTP_201_CREATED,
        )


# ----------------------------------------------------------------
# PENALTY
# ----------------------------------------------------------------

class ApplyPenaltyView(APIView):
    """POST /api/writer-management/writers/<rid>/penalties/"""
    permission_classes = [IsAdminUser]

    def post(self, request, registration_id):
        writer = _get_writer_or_404(registration_id)
        if writer is None:
            return Response({"detail": "Writer not found."}, status=404)
        serializer = ApplyPenaltySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        penalty = DisciplineService.apply_penalty(
            writer=writer,
            reason=d["reason"],
            amount=d["amount"],
            order=None,
            applied_by=request.user,
            notes=d.get("notes", ""),
        )
        return Response(
            WriterPenaltySerializer(penalty).data,
            status=status.HTTP_201_CREATED,
        )