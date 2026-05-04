from __future__ import annotations

from django.contrib import admin

from class_management.models import (
    ClassAccessDetail,
    ClassAccessGrant,
    ClassAccessLog,
    ClassAssignment,
    ClassInstallment,
    ClassInstallmentPlan,
    ClassInvoiceLink,
    ClassOrder,
    ClassPaymentAllocation,
    ClassPortalWorkLog,
    ClassPriceCounterOffer,
    ClassPriceProposal,
    ClassScopeAssessment,
    ClassScopeItem,
    ClassTask,
    ClassTimelineEvent,
    ClassTwoFactorRequest,
    ClassTwoFactorWindow,
    ClassWriterCompensation,
)


class ClassTwoFactorWindowInline(admin.TabularInline):
    """
    Inline 2FA availability windows for class access details.
    """

    model = ClassTwoFactorWindow
    extra = 0


class ClassInstallmentInline(admin.TabularInline):
    """
    Inline installments under an installment plan.
    """

    model = ClassInstallment
    extra = 0
    readonly_fields = [
        "paid_amount",
        "paid_at",
        "created_at",
        "updated_at",
    ]


class ClassScopeItemInline(admin.TabularInline):
    """
    Inline workload scope items under a class order.
    """

    model = ClassScopeItem
    extra = 0


class ClassTaskInline(admin.TabularInline):
    """
    Inline class tasks under a class order.
    """

    model = ClassTask
    extra = 0


class ClassTimelineEventInline(admin.TabularInline):
    """
    Inline timeline events under a class order.
    """

    model = ClassTimelineEvent
    extra = 0
    can_delete = False
    readonly_fields = [
        "event_type",
        "title",
        "description",
        "triggered_by",
        "metadata",
        "created_at",
    ]

    def has_add_permission(self, request, obj=None) -> bool:
        """
        Timeline events should be created by services.
        """
        return False


@admin.register(ClassOrder)
class ClassOrderAdmin(admin.ModelAdmin):
    """
    Admin for class orders.
    """

    list_display = [
        "id",
        "title",
        "website",
        "client",
        "assigned_writer",
        "status",
        "payment_status",
        "final_amount",
        "paid_amount",
        "balance_amount",
        "currency",
        "created_at",
    ]
    list_filter = [
        "website",
        "status",
        "payment_status",
        "complexity_level",
        "currency",
        "created_at",
    ]
    search_fields = [
        "title",
        "client__email",
        "client__username",
        "assigned_writer__email",
        "assigned_writer__username",
        "institution_name",
        "class_name",
        "class_code",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
        "submitted_at",
        "accepted_at",
        "completed_at",
        "cancelled_at",
        "archived_at",
    ]
    autocomplete_fields = [
        "website",
        "client",
        "assigned_writer",
        "created_by",
        "updated_by",
    ]
    fieldsets = [
        (
            "Core",
            {
                "fields": [
                    "website",
                    "client",
                    "assigned_writer",
                    "title",
                    "status",
                    "payment_status",
                    "complexity_level",
                ]
            },
        ),
        (
            "Class Details",
            {
                "fields": [
                    "institution_name",
                    "institution_state",
                    "class_name",
                    "class_code",
                    "class_subject",
                    "academic_level",
                    "starts_on",
                    "ends_on",
                ]
            },
        ),
        (
            "Notes",
            {
                "fields": [
                    "initial_client_notes",
                    "writer_visible_notes",
                    "admin_internal_notes",
                ]
            },
        ),
        (
            "Money",
            {
                "fields": [
                    "quoted_amount",
                    "accepted_amount",
                    "discount_code",
                    "discount_amount",
                    "final_amount",
                    "paid_amount",
                    "balance_amount",
                    "currency",
                    "pricing_snapshot",
                    "discount_snapshot",
                ]
            },
        ),
        (
            "Pause State",
            {
                "fields": [
                    "is_work_paused",
                    "pause_reason",
                    "paused_at",
                ]
            },
        ),
        (
            "Audit",
            {
                "fields": [
                    "created_by",
                    "updated_by",
                    "submitted_at",
                    "accepted_at",
                    "completed_at",
                    "cancelled_at",
                    "archived_at",
                    "created_at",
                    "updated_at",
                ]
            },
        ),
    ]
    inlines = [
        ClassScopeItemInline,
        ClassTaskInline,
        ClassTimelineEventInline,
    ]


@admin.register(ClassScopeAssessment)
class ClassScopeAssessmentAdmin(admin.ModelAdmin):
    """
    Admin for workload assessments.
    """

    list_display = [
        "id",
        "class_order",
        "complexity_level",
        "estimated_hours",
        "assessed_by",
        "assessed_at",
    ]
    list_filter = [
        "complexity_level",
        "assessed_at",
    ]
    search_fields = [
        "class_order__title",
        "assessed_by__email",
        "assessed_by__username",
    ]
    autocomplete_fields = [
        "class_order",
        "assessed_by",
    ]


@admin.register(ClassScopeItem)
class ClassScopeItemAdmin(admin.ModelAdmin):
    """
    Admin for class scope items.
    """

    list_display = [
        "id",
        "class_order",
        "item_type",
        "title",
        "quantity",
        "due_at",
        "complexity_level",
    ]
    list_filter = [
        "item_type",
        "complexity_level",
        "due_at",
    ]
    search_fields = [
        "title",
        "class_order__title",
        "notes",
    ]
    autocomplete_fields = [
        "class_order",
        "created_by",
    ]


@admin.register(ClassTask)
class ClassTaskAdmin(admin.ModelAdmin):
    """
    Admin for class tasks.
    """

    list_display = [
        "id",
        "class_order",
        "title",
        "assigned_writer",
        "status",
        "due_at",
        "requires_portal_work",
        "portal_submission_required",
    ]
    list_filter = [
        "status",
        "requires_portal_work",
        "portal_submission_required",
        "due_at",
    ]
    search_fields = [
        "title",
        "description",
        "class_order__title",
        "assigned_writer__email",
        "assigned_writer__username",
    ]
    autocomplete_fields = [
        "class_order",
        "scope_item",
        "assigned_writer",
        "created_by",
    ]


@admin.register(ClassAccessDetail)
class ClassAccessDetailAdmin(admin.ModelAdmin):
    """
    Admin for protected class access details.

    Sensitive fields should still be viewed through services in the app.
    """

    list_display = [
        "id",
        "class_order",
        "institution_name",
        "class_name",
        "requires_two_factor",
        "updated_at",
    ]
    list_filter = [
        "requires_two_factor",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "class_order__title",
        "institution_name",
        "class_name",
        "class_code",
        "login_username",
    ]
    autocomplete_fields = [
        "class_order",
        "created_by",
        "updated_by",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    inlines = [
        ClassTwoFactorWindowInline,
    ]


@admin.register(ClassAccessGrant)
class ClassAccessGrantAdmin(admin.ModelAdmin):
    """
    Admin for access grants.
    """

    list_display = [
        "id",
        "class_order",
        "user",
        "status",
        "granted_by",
        "granted_at",
        "expires_at",
        "revoked_at",
    ]
    list_filter = [
        "status",
        "granted_at",
        "expires_at",
    ]
    search_fields = [
        "class_order__title",
        "user__email",
        "user__username",
        "granted_by__email",
        "granted_by__username",
    ]
    autocomplete_fields = [
        "class_order",
        "user",
        "granted_by",
    ]


@admin.register(ClassAccessLog)
class ClassAccessLogAdmin(admin.ModelAdmin):
    """
    Read-only admin for access audit logs.
    """

    list_display = [
        "id",
        "class_order",
        "viewed_by",
        "ip_address",
        "viewed_at",
    ]
    list_filter = [
        "viewed_at",
    ]
    search_fields = [
        "class_order__title",
        "viewed_by__email",
        "viewed_by__username",
        "reason",
        "ip_address",
    ]
    readonly_fields = [
        "class_order",
        "viewed_by",
        "reason",
        "ip_address",
        "user_agent",
        "viewed_at",
    ]

    def has_add_permission(self, request) -> bool:
        """
        Logs should only be created by services.
        """
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        """
        Logs should not be modified manually.
        """
        return False


@admin.register(ClassTwoFactorRequest)
class ClassTwoFactorRequestAdmin(admin.ModelAdmin):
    """
    Admin for 2FA coordination requests.
    """

    list_display = [
        "id",
        "class_order",
        "requested_by",
        "status",
        "needed_by",
        "requested_at",
        "resolved_at",
    ]
    list_filter = [
        "status",
        "needed_by",
        "requested_at",
    ]
    search_fields = [
        "class_order__title",
        "requested_by__email",
        "requested_by__username",
        "request_notes",
    ]
    autocomplete_fields = [
        "class_order",
        "requested_by",
    ]


@admin.register(ClassTwoFactorWindow)
class ClassTwoFactorWindowAdmin(admin.ModelAdmin):
    """
    Admin for 2FA availability windows.
    """

    list_display = [
        "id",
        "access_detail",
        "weekday",
        "starts_at",
        "ends_at",
        "timezone",
        "is_active",
    ]
    list_filter = [
        "weekday",
        "timezone",
        "is_active",
    ]
    autocomplete_fields = [
        "access_detail",
    ]


@admin.register(ClassPriceProposal)
class ClassPriceProposalAdmin(admin.ModelAdmin):
    """
    Admin for class price proposals.
    """

    list_display = [
        "id",
        "class_order",
        "amount",
        "discount_amount",
        "final_amount",
        "currency",
        "status",
        "proposed_by",
        "sent_at",
        "accepted_at",
    ]
    list_filter = [
        "status",
        "currency",
        "sent_at",
        "accepted_at",
        "created_at",
    ]
    search_fields = [
        "class_order__title",
        "message_to_client",
        "internal_notes",
        "proposed_by__email",
        "proposed_by__username",
    ]
    autocomplete_fields = [
        "class_order",
        "proposed_by",
        "accepted_by",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]


@admin.register(ClassPriceCounterOffer)
class ClassPriceCounterOfferAdmin(admin.ModelAdmin):
    """
    Admin for class price counter offers.
    """

    list_display = [
        "id",
        "proposal",
        "offered_amount",
        "created_by",
        "created_at",
    ]
    list_filter = [
        "created_at",
    ]
    search_fields = [
        "proposal__class_order__title",
        "message",
        "created_by__email",
        "created_by__username",
    ]
    autocomplete_fields = [
        "proposal",
        "created_by",
    ]


@admin.register(ClassInstallmentPlan)
class ClassInstallmentPlanAdmin(admin.ModelAdmin):
    """
    Admin for class installment plans.
    """

    list_display = [
        "id",
        "class_order",
        "total_amount",
        "deposit_amount",
        "installment_count",
        "allow_work_before_full_payment",
        "pause_work_when_overdue",
        "created_at",
    ]
    list_filter = [
        "allow_work_before_full_payment",
        "pause_work_when_overdue",
        "created_at",
    ]
    search_fields = [
        "class_order__title",
        "notes",
    ]
    autocomplete_fields = [
        "class_order",
    ]
    inlines = [
        ClassInstallmentInline,
    ]


@admin.register(ClassInstallment)
class ClassInstallmentAdmin(admin.ModelAdmin):
    """
    Admin for class installments.
    """

    list_display = [
        "id",
        "plan",
        "label",
        "amount",
        "paid_amount",
        "status",
        "due_at",
        "paid_at",
    ]
    list_filter = [
        "status",
        "due_at",
        "paid_at",
    ]
    search_fields = [
        "plan__class_order__title",
        "label",
        "payment_intent_id",
        "invoice_id",
    ]
    autocomplete_fields = [
        "plan",
    ]


@admin.register(ClassInvoiceLink)
class ClassInvoiceLinkAdmin(admin.ModelAdmin):
    """
    Admin for class invoice links.
    """

    list_display = [
        "id",
        "class_order",
        "invoice_id",
        "invoice_number",
        "status",
        "created_at",
    ]
    list_filter = [
        "status",
        "created_at",
    ]
    search_fields = [
        "class_order__title",
        "invoice_id",
        "invoice_number",
    ]
    autocomplete_fields = [
        "class_order",
    ]


@admin.register(ClassPaymentAllocation)
class ClassPaymentAllocationAdmin(admin.ModelAdmin):
    """
    Admin for class payment allocations.
    """

    list_display = [
        "id",
        "class_order",
        "source_type",
        "amount",
        "wallet_amount",
        "external_amount",
        "payment_intent_id",
        "created_at",
    ]
    list_filter = [
        "source_type",
        "created_at",
    ]
    search_fields = [
        "class_order__title",
        "payment_intent_id",
        "payment_transaction_id",
        "wallet_transaction_id",
        "ledger_entry_id",
        "reference",
    ]
    autocomplete_fields = [
        "class_order",
        "installment",
    ]


@admin.register(ClassAssignment)
class ClassAssignmentAdmin(admin.ModelAdmin):
    """
    Admin for class writer assignments.
    """

    list_display = [
        "id",
        "class_order",
        "writer",
        "status",
        "assigned_by",
        "assigned_at",
        "removed_at",
    ]
    list_filter = [
        "status",
        "assigned_at",
        "removed_at",
    ]
    search_fields = [
        "class_order__title",
        "writer__email",
        "writer__username",
        "assigned_by__email",
        "assigned_by__username",
    ]
    autocomplete_fields = [
        "class_order",
        "writer",
        "assigned_by",
    ]


@admin.register(ClassWriterCompensation)
class ClassWriterCompensationAdmin(admin.ModelAdmin):
    """
    Admin for writer compensation.
    """

    list_display = [
        "id",
        "class_order",
        "writer",
        "compensation_type",
        "final_amount",
        "paid_amount",
        "status",
        "approved_at",
        "earned_at",
        "posted_at",
    ]
    list_filter = [
        "compensation_type",
        "status",
        "approved_at",
        "earned_at",
        "posted_at",
    ]
    search_fields = [
        "class_order__title",
        "writer__email",
        "writer__username",
        "wallet_transaction_id",
        "ledger_entry_id",
    ]
    autocomplete_fields = [
        "class_order",
        "writer",
        "approved_by",
        "posted_by",
    ]


@admin.register(ClassPortalWorkLog)
class ClassPortalWorkLogAdmin(admin.ModelAdmin):
    """
    Admin for portal work logs.
    """

    list_display = [
        "id",
        "class_order",
        "writer",
        "activity_type",
        "title",
        "visible_to_client",
        "verification_status",
        "occurred_at",
        "logged_at",
    ]
    list_filter = [
        "activity_type",
        "visible_to_client",
        "verification_status",
        "occurred_at",
        "logged_at",
    ]
    search_fields = [
        "class_order__title",
        "writer__email",
        "writer__username",
        "title",
        "description",
        "portal_reference",
    ]
    autocomplete_fields = [
        "class_order",
        "task",
        "writer",
        "verified_by",
    ]


@admin.register(ClassTimelineEvent)
class ClassTimelineEventAdmin(admin.ModelAdmin):
    """
    Read-only admin for class timeline events.
    """

    list_display = [
        "id",
        "class_order",
        "event_type",
        "title",
        "triggered_by",
        "created_at",
    ]
    list_filter = [
        "event_type",
        "created_at",
    ]
    search_fields = [
        "class_order__title",
        "title",
        "description",
        "triggered_by__email",
        "triggered_by__username",
    ]
    readonly_fields = [
        "class_order",
        "event_type",
        "title",
        "description",
        "triggered_by",
        "metadata",
        "created_at",
    ]
    autocomplete_fields = [
        "class_order",
        "triggered_by",
    ]

    def has_add_permission(self, request) -> bool:
        """
        Timeline events should only be created by services.
        """
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        """
        Timeline events should not be modified manually.
        """
        return False