from __future__ import annotations

from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from class_management.analytics.class_dashboard_metrics import (
    ClassDashboardMetrics,
)
from class_management.analytics.class_risk_metrics import ClassRiskMetrics
from class_management.analytics.class_workload_metrics import (
    ClassWorkloadMetrics,
)
from class_management.analytics.class_writer_metrics import ClassWriterMetrics
from class_management.api.serializers.class_dashboard_serializers import (
    ClassDashboardSummarySerializer,
)


class ClassDashboardView(APIView):
    """
    Admin dashboard for class management.
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        website = request.website

        summary = ClassDashboardMetrics.get_summary(website=website)

        payload = {
            "summary": ClassDashboardSummarySerializer(summary).data,
            "workload": {
                "item_type_breakdown": list(
                    ClassWorkloadMetrics.item_type_breakdown(
                        website=website,
                    )
                ),
                "task_status_breakdown": list(
                    ClassWorkloadMetrics.task_status_breakdown(
                        website=website,
                    )
                ),
            },
            "writers": {
                "assignment_summary": list(
                    ClassWriterMetrics.writer_assignment_summary(
                        website=website,
                    )
                ),
                "task_summary": list(
                    ClassWriterMetrics.writer_task_summary(
                        website=website,
                    )
                ),
                "compensation_summary": list(
                    ClassWriterMetrics.writer_compensation_summary(
                        website=website,
                    )
                ),
            },
            "risk": {
                "paused_classes": ClassRiskMetrics.paused_classes(
                    website=website,
                ).count(),
                "overdue_installments": ClassRiskMetrics.overdue_installments(
                    website=website,
                ).count(),
                "overdue_tasks": ClassRiskMetrics.overdue_tasks(
                    website=website,
                ).count(),
                "pending_two_factor_requests": (
                    ClassRiskMetrics.pending_two_factor_requests(
                        website=website,
                    ).count()
                ),
            "portal_activity_breakdown": list(
                ClassWorkloadMetrics.portal_activity_breakdown(website=website)
            ),
            },
        }

        return Response(payload)