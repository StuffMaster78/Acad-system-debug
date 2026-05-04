from __future__ import annotations

from typing import cast, Any
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets

from class_management.api.permissions.class_timeline_permissions import (
    ClassTimelinePermission,
)
from class_management.api.serializers.class_timeline_serializers import (
    ClassTimelineEventSerializer,
)
from class_management.selectors.class_order_selectors import (
    ClassOrderSelector,
)
from class_management.selectors.class_timeline_selectors import (
    ClassTimelineSelector,
)
from class_management.api.views.class_base_views import ClassTenantViewMixin


class ClassTimelineViewSet(ClassTenantViewMixin, viewsets.GenericViewSet):
    """
    API endpoints for class timeline events.
    """

    permission_classes = [IsAuthenticated, ClassTimelinePermission]

    def get_class_order(self):
        class_order = ClassOrderSelector.get_for_website(
            website=self.get_website(),
            class_order_id=self.kwargs["class_order_pk"],
        )
        self.check_object_permissions(self.request, class_order)
        return class_order

    def list(self, request, *args, **kwargs):
        class_order = self.get_class_order()

        events = ClassTimelineSelector.for_order(
            class_order=class_order,
        )

        return Response(
            ClassTimelineEventSerializer(events, many=True).data
        )