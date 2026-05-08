from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import QuerySet

from audit_logging.api.permissions.audit_permissions import CanManageAuditFailures
from audit_logging.api.serializers.audit_dead_letter_serializer import (
    AuditDeadLetterSerializer,
)
from audit_logging.models.audit_dead_letter import AuditDeadLetter
from audit_logging.services.query.audit_query_policy import AuditQueryPolicy

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter


class AuditDeadLetterViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = AuditDeadLetterSerializer
    permission_classes = (IsAuthenticated, CanManageAuditFailures)

    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter,
    )

    ordering = ("-created_at",)

    def get_queryset(self) -> QuerySet[AuditDeadLetter]:  # type: ignore[override]

        user = self.request.user

        policy = AuditQueryPolicy(user=user)

        qs = policy.user_dlq_backlog()

        return qs