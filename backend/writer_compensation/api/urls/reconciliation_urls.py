from __future__ import annotations

from django.urls import path

from writer_compensation.api.views.reconciliation_actions_views import (
    RunReconciliationView,
)

urlpatterns = [
    path(
        "run/",
        RunReconciliationView.as_view(),
        name="run-reconciliation",
    ),
]