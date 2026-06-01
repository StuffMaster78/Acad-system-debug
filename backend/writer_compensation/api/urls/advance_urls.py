from django.urls import path

from writer_compensation.api.views.advance_views import (
    AdminAdvanceApproveView,
    AdminAdvanceListView,
    AdminAdvanceRecoveryView,
    AdminAdvanceRejectView,
    WriterAdvanceRequestView,
)

urlpatterns = [
    path(
        "",
        WriterAdvanceRequestView.as_view(),
        name="advance-request",
    ),
    path(
        "admin/",
        AdminAdvanceListView.as_view(),
        name="admin-advance-list",
    ),
    path(
        "admin/<int:pk>/approve/",
        AdminAdvanceApproveView.as_view(),
        name="admin-advance-approve",
    ),
    path(
        "admin/<int:pk>/reject/",
        AdminAdvanceRejectView.as_view(),
        name="admin-advance-reject",
    ),
    path(
        "admin/<int:pk>/recover/",
        AdminAdvanceRecoveryView.as_view(),
        name="admin-advance-recovery",
    ),
]