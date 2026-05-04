from __future__ import annotations

from django.urls import path

from class_management.api.views import (
    ClassAccessViewSet,
    ClassAssignmentViewSet,
    ClassOrderViewSet,
    ClassPaymentViewSet,
    ClassPriceProposalViewSet,
    ClassScopeAssessmentViewSet,
    ClassScopeItemViewSet,
    ClassTaskViewSet,
    ClassTimelineViewSet,
    ClassWriterCompensationViewSet,
)
from class_management.api.views.class_dashboard_views import (
    ClassDashboardView,
)

from class_management.api.views.class_portal_work_views import (
    ClassPortalWorkLogViewSet,
)

app_name = "class_management"

class_order_list = ClassOrderViewSet.as_view({
    "get": "list",
    "post": "create",
})
class_order_detail = ClassOrderViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})
class_order_submit = ClassOrderViewSet.as_view({"post": "submit"})
class_order_start_review = ClassOrderViewSet.as_view({"post": "start_review"})
class_order_start_work = ClassOrderViewSet.as_view({"post": "start_work"})
class_order_complete = ClassOrderViewSet.as_view({"post": "complete"})
class_order_cancel = ClassOrderViewSet.as_view({"post": "cancel"})
class_order_archive = ClassOrderViewSet.as_view({"post": "archive"})

scope_assessment = ClassScopeAssessmentViewSet.as_view({
    "get": "retrieve",
    "post": "create",
})
scope_items = ClassScopeItemViewSet.as_view({
    "get": "list",
    "post": "create",
})

tasks = ClassTaskViewSet.as_view({
    "get": "list",
    "post": "create",
})
task_start = ClassTaskViewSet.as_view({"post": "start"})
task_submit = ClassTaskViewSet.as_view({"post": "submit"})
task_complete = ClassTaskViewSet.as_view({"post": "complete"})
task_cancel = ClassTaskViewSet.as_view({"post": "cancel"})

price_proposals = ClassPriceProposalViewSet.as_view({
    "get": "list",
    "post": "create",
})
price_proposal_send = ClassPriceProposalViewSet.as_view({"post": "send"})
price_proposal_accept = ClassPriceProposalViewSet.as_view({"post": "accept"})
price_proposal_reject = ClassPriceProposalViewSet.as_view({"post": "reject"})
price_proposal_counter = ClassPriceProposalViewSet.as_view({"post": "counter"})

access_details = ClassAccessViewSet.as_view({
    "put": "details",
    "patch": "details",
})
access_view_details = ClassAccessViewSet.as_view({"post": "view_details"})
access_two_factor_windows = ClassAccessViewSet.as_view({
    "put": "two_factor_windows",
})
access_grants = ClassAccessViewSet.as_view({"get": "grants"})
access_grant = ClassAccessViewSet.as_view({"post": "grant"})
access_revoke = ClassAccessViewSet.as_view({"post": "revoke"})
access_logs = ClassAccessViewSet.as_view({"get": "logs"})
two_factor_requests = ClassAccessViewSet.as_view({
    "get": "two_factor_requests",
    "post": "request_two_factor",
})
two_factor_sent = ClassAccessViewSet.as_view({"post": "mark_two_factor_sent"})
two_factor_resolve = ClassAccessViewSet.as_view({
    "post": "resolve_two_factor",
})

payment_invoices = ClassPaymentViewSet.as_view({"get": "invoices"})
payment_allocations = ClassPaymentViewSet.as_view({"get": "allocations"})
payment_installments = ClassPaymentViewSet.as_view({"get": "installments"})
payment_create_equal_installments = ClassPaymentViewSet.as_view({
    "post": "create_equal_installments",
})
payment_prepare = ClassPaymentViewSet.as_view({"post": "prepare_payment"})
payment_waive_installment = ClassPaymentViewSet.as_view({
    "post": "waive_installment",
})
payment_resume_work = ClassPaymentViewSet.as_view({"post": "resume_work"})

assignments = ClassAssignmentViewSet.as_view({
    "get": "list",
    "post": "create",
})
assignment_reassign = ClassAssignmentViewSet.as_view({"post": "reassign"})
assignment_remove = ClassAssignmentViewSet.as_view({"post": "remove"})

writer_compensation = ClassWriterCompensationViewSet.as_view({
    "get": "list",
    "post": "create",
})
writer_compensation_approve = ClassWriterCompensationViewSet.as_view({
    "post": "approve",
})
writer_compensation_mark_earned = ClassWriterCompensationViewSet.as_view({
    "post": "mark_earned",
})
writer_compensation_post_to_wallet = (
    ClassWriterCompensationViewSet.as_view({
        "post": "post_to_wallet",
    })
)

timeline = ClassTimelineViewSet.as_view({"get": "list"})

portal_work_logs = ClassPortalWorkLogViewSet.as_view({
    "get": "list",
    "post": "create",
})
portal_work_log_verify = ClassPortalWorkLogViewSet.as_view({
    "post": "verify",
})
portal_work_log_reject = ClassPortalWorkLogViewSet.as_view({
    "post": "reject",
})
scope_item_detail = ClassScopeItemViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

task_detail = ClassTaskViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

price_proposal_detail = ClassPriceProposalViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

urlpatterns = [
    path("classes/", class_order_list, name="class-order-list"),
    path("classes/<int:pk>/", class_order_detail, name="class-order-detail"),
    path(
        "classes/<int:pk>/submit/",
        class_order_submit,
        name="class-order-submit",
    ),
    path(
        "classes/<int:pk>/start-review/",
        class_order_start_review,
        name="class-order-start-review",
    ),
    path(
        "classes/<int:pk>/start-work/",
        class_order_start_work,
        name="class-order-start-work",
    ),
    path(
        "classes/<int:pk>/complete/",
        class_order_complete,
        name="class-order-complete",
    ),
    path(
        "classes/<int:pk>/cancel/",
        class_order_cancel,
        name="class-order-cancel",
    ),
    path(
        "classes/<int:pk>/archive/",
        class_order_archive,
        name="class-order-archive",
    ),

    path(
        "classes/<int:class_order_pk>/scope-assessment/",
        scope_assessment,
        name="class-scope-assessment",
    ),
    path(
        "classes/<int:class_order_pk>/scope-items/",
        scope_items,
        name="class-scope-items",
    ),

    path(
        "classes/<int:class_order_pk>/tasks/",
        tasks,
        name="class-tasks",
    ),
    path(
        "classes/<int:class_order_pk>/tasks/<int:pk>/start/",
        task_start,
        name="class-task-start",
    ),
    path(
        "classes/<int:class_order_pk>/tasks/<int:pk>/submit/",
        task_submit,
        name="class-task-submit",
    ),
    path(
        "classes/<int:class_order_pk>/tasks/<int:pk>/complete/",
        task_complete,
        name="class-task-complete",
    ),
    path(
        "classes/<int:class_order_pk>/tasks/<int:pk>/cancel/",
        task_cancel,
        name="class-task-cancel",
    ),

    path(
        "classes/<int:class_order_pk>/price-proposals/",
        price_proposals,
        name="class-price-proposals",
    ),
    path(
        "classes/<int:class_order_pk>/price-proposals/<int:pk>/send/",
        price_proposal_send,
        name="class-price-proposal-send",
    ),
    path(
        "classes/<int:class_order_pk>/price-proposals/<int:pk>/accept/",
        price_proposal_accept,
        name="class-price-proposal-accept",
    ),
    path(
        "classes/<int:class_order_pk>/price-proposals/<int:pk>/reject/",
        price_proposal_reject,
        name="class-price-proposal-reject",
    ),
    path(
        "classes/<int:class_order_pk>/price-proposals/<int:pk>/counter/",
        price_proposal_counter,
        name="class-price-proposal-counter",
    ),

    path(
        "classes/<int:class_order_pk>/access/details/",
        access_details,
        name="class-access-details",
    ),
    path(
        "classes/<int:class_order_pk>/access/view-details/",
        access_view_details,
        name="class-access-view-details",
    ),
    path(
        "classes/<int:class_order_pk>/access/two-factor-windows/",
        access_two_factor_windows,
        name="class-access-two-factor-windows",
    ),
    path(
        "classes/<int:class_order_pk>/access/grants/",
        access_grants,
        name="class-access-grants",
    ),
    path(
        "classes/<int:class_order_pk>/access/grant/",
        access_grant,
        name="class-access-grant",
    ),
    path(
        "classes/<int:class_order_pk>/access/revoke/",
        access_revoke,
        name="class-access-revoke",
    ),
    path(
        "classes/<int:class_order_pk>/access/logs/",
        access_logs,
        name="class-access-logs",
    ),
    path(
        "classes/<int:class_order_pk>/access/two-factor-requests/",
        two_factor_requests,
        name="class-two-factor-requests",
    ),
    path(
        "classes/<int:class_order_pk>/access/"
        "two-factor-requests/<int:request_id>/sent/",
        two_factor_sent,
        name="class-two-factor-sent",
    ),
    path(
        "classes/<int:class_order_pk>/access/"
        "two-factor-requests/<int:request_id>/resolve/",
        two_factor_resolve,
        name="class-two-factor-resolve",
    ),

    path(
        "classes/<int:class_order_pk>/payments/invoices/",
        payment_invoices,
        name="class-payment-invoices",
    ),
    path(
        "classes/<int:class_order_pk>/payments/allocations/",
        payment_allocations,
        name="class-payment-allocations",
    ),
    path(
        "classes/<int:class_order_pk>/payments/installments/",
        payment_installments,
        name="class-payment-installments",
    ),
    path(
        "classes/<int:class_order_pk>/payments/create-equal-installments/",
        payment_create_equal_installments,
        name="class-payment-create-equal-installments",
    ),
    path(
        "classes/<int:class_order_pk>/payments/prepare/",
        payment_prepare,
        name="class-payment-prepare",
    ),
    path(
        "classes/<int:class_order_pk>/payments/"
        "installments/<int:installment_id>/waive/",
        payment_waive_installment,
        name="class-payment-waive-installment",
    ),
    path(
        "classes/<int:class_order_pk>/payments/resume-work/",
        payment_resume_work,
        name="class-payment-resume-work",
    ),

    path(
        "classes/<int:class_order_pk>/assignments/",
        assignments,
        name="class-assignments",
    ),
    path(
        "classes/<int:class_order_pk>/assignments/reassign/",
        assignment_reassign,
        name="class-assignment-reassign",
    ),
    path(
        "classes/<int:class_order_pk>/assignments/remove/",
        assignment_remove,
        name="class-assignment-remove",
    ),

    path(
        "classes/<int:class_order_pk>/writer-compensation/",
        writer_compensation,
        name="class-writer-compensation",
    ),
    path(
        "classes/<int:class_order_pk>/writer-compensation/approve/",
        writer_compensation_approve,
        name="class-writer-compensation-approve",
    ),
    path(
        "classes/<int:class_order_pk>/writer-compensation/mark-earned/",
        writer_compensation_mark_earned,
        name="class-writer-compensation-mark-earned",
    ),
    path(
        "classes/<int:class_order_pk>/writer-compensation/post-to-wallet/",
        writer_compensation_post_to_wallet,
        name="class-writer-compensation-post-to-wallet",
    ),

    path(
        "classes/<int:class_order_pk>/timeline/",
        timeline,
        name="class-timeline",
    ),
    path(
        "dashboard/",
        ClassDashboardView.as_view(),
        name="class-dashboard",
    ),
    path(
        "classes/<int:class_order_pk>/portal-work-logs/",
        portal_work_logs,
        name="class-portal-work-logs",
    ),
    path(
        "classes/<int:class_order_pk>/portal-work-logs/<int:pk>/verify/",
        portal_work_log_verify,
        name="class-portal-work-log-verify",
    ),
    path(
        "classes/<int:class_order_pk>/portal-work-logs/<int:pk>/reject/",
        portal_work_log_reject,
        name="class-portal-work-log-reject",
    ),
    path(
        "classes/<int:class_order_pk>/scope-items/<int:pk>/",
        scope_item_detail,
        name="class-scope-item-detail",
    ),
    path(
        "classes/<int:class_order_pk>/tasks/<int:pk>/",
        task_detail,
        name="class-task-detail",
    ),
    path(
        "classes/<int:class_order_pk>/price-proposals/<int:pk>/",
        price_proposal_detail,
        name="class-price-proposal-detail",
    ),
]