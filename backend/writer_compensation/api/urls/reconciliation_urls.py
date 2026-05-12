from __future__ import annotations

from django.urls import path

from writer_compensation.api.views.reconciliation_actions_views import (
    RunReconciliationView,
    ReconciliationReportListView,
)

urlpatterns = [
    path(
        "",
        ReconciliationReportListView.as_view(),
        name="reconciliation-list",
    ),
    path(
        "run/",
        RunReconciliationView.as_view(),
        name="run-reconciliation",
    ),
]