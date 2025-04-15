from django.urls import path
from authentication.views.deletion import (
    RequestDeletionView,
    DeletionRequestStatusView,
    AdminApproveDeletionView,
    AdminRejectDeletionView,
)

urlpatterns = [
    path(
        'request-deletion/',
        RequestDeletionView.as_view(),
        name='request_deletion'
    ),
    path(
        'deletion-request-status/<int:request_id>/',
        DeletionRequestStatusView.as_view(),
        name='deletion_request_status'
    ),
    path(
        'admin/approve-deletion/<int:request_id>/',
        AdminApproveDeletionView.as_view(),
        name='admin_approve_deletion'
    ),
    path(
        'admin/reject-deletion/<int:request_id>/',
        AdminRejectDeletionView.as_view(),
        name='admin_reject_deletion'
    ),
]