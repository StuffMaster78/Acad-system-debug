from __future__ import annotations

from django.contrib import admin

from special_orders.models import (
    EstimatedSpecialOrderSettings,
    PredefinedSpecialOrderConfig,
    PredefinedSpecialOrderDuration,
    SpecialOrder,
    SpecialOrderAccessGrant,
    SpecialOrderAccessLog,
    SpecialOrderAdminOverride,
    SpecialOrderAnalyticsEvent,
    SpecialOrderChangeRequest,
    SpecialOrderChangeRequestQuote,
    SpecialOrderCompletionLog,
    SpecialOrderDeliverable,
    SpecialOrderDeliveryCheckpoint,
    SpecialOrderDiscountApplication,
    SpecialOrderDiscountRule,
    SpecialOrderDispute,
    SpecialOrderDisputeResolution,
    SpecialOrderExternalLink,
    SpecialOrderFundingMilestone,
    SpecialOrderFundingPlan,
    SpecialOrderInstitutionProfile,
    SpecialOrderMilestoneTemplate,
    SpecialOrderMilestoneTemplateItem,
    SpecialOrderPaymentApplication,
    SpecialOrderPlatformAccessVault,
    SpecialOrderPricingSnapshot,
    SpecialOrderQuote,
    SpecialOrderQuoteLine,
    SpecialOrderRefundApplication,
    SpecialOrderStatusHistory,
    SpecialOrderTwoFactorRequest,
    SpecialOrderWriterPayRule,
)
from special_orders.models.configs import (
    SpecialOrderCapacityRule,
    SpecialOrderCurrencyPriceOverride,
    SpecialOrderPlatformDifficultyRule,
    SpecialOrderRushSurchargeRule,
    SpecialOrderWriterLevelSurchargeRule,
)

class PredefinedSpecialOrderDurationInline(admin.TabularInline):
    model = PredefinedSpecialOrderDuration
    extra = 0
    fields = (
        "duration_days",
        "price",
        "is_active",
    )


@admin.register(PredefinedSpecialOrderConfig)
class PredefinedSpecialOrderConfigAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "website",
        "slug",
        "is_active",
        "requires_full_payment",
        "allow_wallet_payment",
        "allow_external_payment",
    )
    list_filter = (
        "website",
        "is_active",
        "requires_full_payment",
        "allow_wallet_payment",
        "allow_external_payment",
    )
    search_fields = (
        "name",
        "slug",
        "description",
    )
    prepopulated_fields = {
        "slug": ("name",),
    }
    inlines = [PredefinedSpecialOrderDurationInline]


@admin.register(PredefinedSpecialOrderDuration)
class PredefinedSpecialOrderDurationAdmin(admin.ModelAdmin):
    list_display = (
        "predefined_order",
        "website",
        "duration_days",
        "price",
        "is_active",
    )
    list_filter = (
        "website",
        "is_active",
        "duration_days",
    )
    search_fields = (
        "predefined_order__name",
    )


@admin.register(EstimatedSpecialOrderSettings)
class EstimatedSpecialOrderSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "website",
        "default_deposit_percentage",
        "minimum_deposit_amount",
        "allow_installments",
        "require_deposit_before_staffing",
        "require_full_payment_before_delivery",
    )
    list_filter = (
        "website",
        "allow_installments",
        "require_deposit_before_staffing",
        "require_full_payment_before_delivery",
    )


class SpecialOrderStatusHistoryInline(admin.TabularInline):
    model = SpecialOrderStatusHistory
    extra = 0
    readonly_fields = (
        "previous_status",
        "new_status",
        "reason",
        "changed_by",
        "metadata",
        "created_at",
    )
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(SpecialOrder)
class SpecialOrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "website",
        "client",
        "writer",
        "pricing_mode",
        "status",
        "priority",
        "currency",
        "created_at",
    )
    list_filter = (
        "website",
        "pricing_mode",
        "status",
        "priority",
        "origin",
        "created_at",
    )
    search_fields = (
        "id",
        "title",
        "client__email",
        "writer__email",
        "inquiry_details",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "assigned_at",
        "started_at",
        "completed_at",
        "cancelled_at",
    )
    raw_id_fields = (
        "client",
        "writer",
        "predefined_config",
        "predefined_duration",
        "writer_pay_rule",
        "accepted_quote",
        "converted_order",
    )
    inlines = [SpecialOrderStatusHistoryInline]


class SpecialOrderQuoteLineInline(admin.TabularInline):
    model = SpecialOrderQuoteLine
    extra = 0
    readonly_fields = (
        "line_type",
        "description",
        "quantity",
        "unit_price",
        "total_price",
        "created_at",
    )

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(SpecialOrderQuote)
class SpecialOrderQuoteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "special_order",
        "website",
        "status",
        "currency",
        "total_amount",
        "discount_amount",
        "expires_at",
    )
    list_filter = (
        "website",
        "status",
        "currency",
        "expires_at",
    )
    search_fields = (
        "special_order__title",
        "special_order__client__email",
    )
    raw_id_fields = (
        "special_order",
        "created_by",
    )
    inlines = [SpecialOrderQuoteLineInline]


@admin.register(SpecialOrderPricingSnapshot)
class SpecialOrderPricingSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "special_order",
        "website",
        "currency",
        "total_amount",
        "deposit_amount",
        "created_at",
    )
    list_filter = (
        "website",
        "currency",
        "created_at",
    )
    search_fields = (
        "special_order__title",
        "special_order__client__email",
    )
    readonly_fields = (
        "raw_data",
        "created_at",
        "updated_at",
    )
    raw_id_fields = (
        "special_order",
    )


class SpecialOrderFundingMilestoneInline(admin.TabularInline):
    model = SpecialOrderFundingMilestone
    extra = 0
    readonly_fields = (
        "funded_amount",
        "refunded_amount",
        "status",
        "created_at",
        "updated_at",
    )


@admin.register(SpecialOrderFundingPlan)
class SpecialOrderFundingPlanAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "special_order",
        "website",
        "status",
        "currency",
        "total_amount",
        "deposit_amount",
        "funded_amount",
        "refunded_amount",
    )
    list_filter = (
        "website",
        "status",
        "currency",
        "requires_full_payment_before_staffing",
        "requires_full_payment_before_delivery",
    )
    search_fields = (
        "special_order__title",
        "special_order__client__email",
    )
    readonly_fields = (
        "funded_amount",
        "refunded_amount",
        "locked_at",
        "metadata",
        "created_at",
        "updated_at",
    )
    raw_id_fields = (
        "special_order",
        "locked_by",
    )
    inlines = [SpecialOrderFundingMilestoneInline]


@admin.register(SpecialOrderPaymentApplication)
class SpecialOrderPaymentApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "special_order",
        "website",
        "source",
        "status",
        "amount",
        "currency",
        "applied_at",
    )
    list_filter = (
        "website",
        "source",
        "status",
        "currency",
        "applied_at",
    )
    search_fields = (
        "idempotency_key",
        "payment_intent_reference",
        "payment_transaction_reference",
        "wallet_transaction_reference",
        "ledger_entry_reference",
        "special_order__title",
    )
    readonly_fields = (
        "idempotency_key",
        "payment_intent_reference",
        "payment_transaction_reference",
        "wallet_transaction_reference",
        "ledger_entry_reference",
        "metadata",
        "applied_at",
        "created_at",
        "updated_at",
    )
    raw_id_fields = (
        "special_order",
        "funding_plan",
        "milestone",
        "applied_by",
    )


@admin.register(SpecialOrderRefundApplication)
class SpecialOrderRefundApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "special_order",
        "website",
        "status",
        "destination",
        "amount",
        "currency",
        "refunded_at",
    )
    list_filter = (
        "website",
        "status",
        "destination",
        "currency",
        "refunded_at",
    )
    search_fields = (
        "refund_transaction_reference",
        "reversal_ledger_entry_reference",
        "reason",
        "special_order__title",
    )
    readonly_fields = (
        "refund_transaction_reference",
        "reversal_ledger_entry_reference",
        "metadata",
        "refunded_at",
        "created_at",
        "updated_at",
    )
    raw_id_fields = (
        "special_order",
        "funding_plan",
        "milestone",
        "original_payment_application",
        "requested_by",
        "approved_by",
    )


@admin.register(SpecialOrderDiscountRule)
class SpecialOrderDiscountRuleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "website",
        "code",
        "discount_type",
        "scope",
        "status",
        "value",
        "usage_count",
    )
    list_filter = (
        "website",
        "discount_type",
        "scope",
        "status",
        "is_stackable",
    )
    search_fields = (
        "name",
        "code",
    )


@admin.register(SpecialOrderDiscountApplication)
class SpecialOrderDiscountApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "special_order",
        "website",
        "discount_type",
        "status",
        "code",
        "amount_applied",
    )
    list_filter = (
        "website",
        "discount_type",
        "status",
    )
    search_fields = (
        "code",
        "reason",
        "special_order__title",
    )
    raw_id_fields = (
        "special_order",
        "quote",
        "discount_rule",
        "approved_by",
        "applied_by",
    )


@admin.register(SpecialOrderChangeRequest)
class SpecialOrderChangeRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "special_order",
        "website",
        "status",
        "pricing_impact",
        "title",
        "approved_amount",
    )
    list_filter = (
        "website",
        "status",
        "pricing_impact",
    )
    search_fields = (
        "title",
        "description",
        "special_order__title",
    )
    raw_id_fields = (
        "special_order",
        "requested_by",
        "reviewed_by",
    )


@admin.register(SpecialOrderChangeRequestQuote)
class SpecialOrderChangeRequestQuoteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "change_request",
        "website",
        "amount",
        "currency",
        "expires_at",
        "accepted_at",
    )
    list_filter = (
        "website",
        "currency",
        "expires_at",
        "accepted_at",
    )
    raw_id_fields = (
        "change_request",
        "created_by",
    )


@admin.register(SpecialOrderDeliveryCheckpoint)
class SpecialOrderDeliveryCheckpointAdmin(admin.ModelAdmin):
    list_display = (
        "special_order",
        "website",
        "checkpoint_type",
        "status",
        "required_milestone",
        "unlocked_at",
    )
    list_filter = (
        "website",
        "checkpoint_type",
        "status",
    )
    raw_id_fields = (
        "special_order",
        "required_milestone",
        "unlocked_by",
    )


@admin.register(SpecialOrderDeliverable)
class SpecialOrderDeliverableAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "special_order",
        "website",
        "title",
        "status",
        "uploaded_by",
        "uploaded_at",
        "delivered_at",
    )
    list_filter = (
        "website",
        "status",
        "uploaded_at",
        "delivered_at",
    )
    search_fields = (
        "title",
        "description",
        "file_reference",
        "special_order__title",
    )
    raw_id_fields = (
        "special_order",
        "uploaded_by",
        "reviewed_by",
    )


@admin.register(SpecialOrderCompletionLog)
class SpecialOrderCompletionLogAdmin(admin.ModelAdmin):
    list_display = (
        "special_order",
        "website",
        "action",
        "completed_by",
        "created_at",
    )
    list_filter = (
        "website",
        "action",
        "created_at",
    )
    search_fields = (
        "action",
        "justification",
        "special_order__title",
    )
    readonly_fields = (
        "metadata",
        "created_at",
        "updated_at",
    )
    raw_id_fields = (
        "special_order",
        "completed_by",
    )


@admin.register(SpecialOrderDispute)
class SpecialOrderDisputeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "special_order",
        "website",
        "status",
        "title",
        "opened_by",
        "assigned_to",
        "opened_at",
        "resolved_at",
    )
    list_filter = (
        "website",
        "status",
        "opened_at",
        "resolved_at",
    )
    search_fields = (
        "title",
        "description",
        "special_order__title",
    )
    raw_id_fields = (
        "special_order",
        "opened_by",
        "assigned_to",
    )


@admin.register(SpecialOrderDisputeResolution)
class SpecialOrderDisputeResolutionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "dispute",
        "special_order",
        "website",
        "resolution_type",
        "amount",
        "currency",
    )
    list_filter = (
        "website",
        "resolution_type",
        "currency",
    )
    search_fields = (
        "notes",
        "special_order__title",
    )
    raw_id_fields = (
        "dispute",
        "special_order",
        "resolved_by",
        "refund_application",
    )


@admin.register(SpecialOrderAdminOverride)
class SpecialOrderAdminOverrideAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "special_order",
        "website",
        "override_type",
        "status",
        "amount",
        "requested_by",
        "approved_by",
        "applied_by",
    )
    list_filter = (
        "website",
        "override_type",
        "status",
        "created_at",
    )
    search_fields = (
        "reason",
        "ledger_entry_reference",
        "special_order__title",
    )
    readonly_fields = (
        "metadata",
        "approved_at",
        "applied_at",
        "reversed_at",
        "created_at",
        "updated_at",
    )
    raw_id_fields = (
        "special_order",
        "requested_by",
        "approved_by",
        "applied_by",
        "payment_application",
        "delivery_checkpoint",
    )


@admin.register(SpecialOrderInstitutionProfile)
class SpecialOrderInstitutionProfileAdmin(admin.ModelAdmin):
    list_display = (
        "institution_name",
        "website",
        "institution_type",
        "program_name",
        "course_code",
        "course_name",
    )
    list_filter = (
        "website",
        "institution_type",
        "country",
        "program_name",
    )
    search_fields = (
        "institution_name",
        "program_name",
        "course_code",
        "course_name",
        "instructor_name",
    )
    raw_id_fields = (
        "special_order",
    )


@admin.register(SpecialOrderPlatformAccessVault)
class SpecialOrderPlatformAccessVaultAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "special_order",
        "website",
        "platform",
        "username",
        "requires_2fa",
        "is_active",
        "created_by",
    )
    list_filter = (
        "website",
        "platform",
        "requires_2fa",
        "is_active",
    )
    search_fields = (
        "special_order__title",
        "platform_label",
        "login_url",
        "username",
    )
    readonly_fields = (
        "encrypted_password",
        "metadata",
        "last_rotated_at",
        "created_at",
        "updated_at",
    )
    raw_id_fields = (
        "special_order",
        "created_by",
    )


@admin.register(SpecialOrderExternalLink)
class SpecialOrderExternalLinkAdmin(admin.ModelAdmin):
    list_display = (
        "label",
        "special_order",
        "website",
        "link_type",
        "requires_login",
        "created_by",
    )
    list_filter = (
        "website",
        "link_type",
        "requires_login",
    )
    search_fields = (
        "label",
        "url",
        "notes",
        "special_order__title",
    )
    raw_id_fields = (
        "special_order",
        "created_by",
    )


@admin.register(SpecialOrderAccessGrant)
class SpecialOrderAccessGrantAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "vault",
        "website",
        "granted_to",
        "access_level",
        "granted_by",
        "expires_at",
        "revoked_at",
    )
    list_filter = (
        "website",
        "access_level",
        "expires_at",
        "revoked_at",
    )
    search_fields = (
        "reason",
        "granted_to__email",
        "granted_by__email",
    )
    raw_id_fields = (
        "vault",
        "special_order",
        "granted_to",
        "granted_by",
        "revoked_by",
    )


@admin.register(SpecialOrderAccessLog)
class SpecialOrderAccessLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "vault",
        "website",
        "action",
        "accessed_by",
        "ip_address",
        "created_at",
    )
    list_filter = (
        "website",
        "action",
        "created_at",
    )
    search_fields = (
        "accessed_by__email",
        "ip_address",
        "user_agent",
    )
    readonly_fields = (
        "vault",
        "special_order",
        "accessed_by",
        "action",
        "ip_address",
        "user_agent",
        "metadata",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SpecialOrderTwoFactorRequest)
class SpecialOrderTwoFactorRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "special_order",
        "website",
        "vault",
        "status",
        "requested_by",
        "client",
        "expires_at",
        "completed_at",
    )
    list_filter = (
        "website",
        "status",
        "preferred_method",
        "expires_at",
        "completed_at",
    )
    search_fields = (
        "message",
        "client__email",
        "requested_by__email",
    )
    raw_id_fields = (
        "special_order",
        "vault",
        "requested_by",
        "client",
    )


@admin.register(SpecialOrderMilestoneTemplate)
class SpecialOrderMilestoneTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "website",
        "is_active",
    )
    list_filter = (
        "website",
        "is_active",
    )
    search_fields = (
        "name",
        "description",
    )


@admin.register(SpecialOrderMilestoneTemplateItem)
class SpecialOrderMilestoneTemplateItemAdmin(admin.ModelAdmin):
    list_display = (
        "template",
        "sequence",
        "label",
        "percentage",
        "required_before_staffing",
        "required_before_delivery",
    )
    list_filter = (
        "template__website",
        "required_before_staffing",
        "required_before_delivery",
    )
    search_fields = (
        "template__name",
        "label",
    )


@admin.register(SpecialOrderWriterPayRule)
class SpecialOrderWriterPayRuleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "website",
        "is_active",
        "fixed_amount",
        "percentage",
    )
    list_filter = (
        "website",
        "is_active",
    )
    search_fields = (
        "name",
    )


@admin.register(SpecialOrderAnalyticsEvent)
class SpecialOrderAnalyticsEventAdmin(admin.ModelAdmin):
    list_display = (
        "event_type",
        "website",
        "conversion_stage",
        "special_order",
        "actor",
        "amount",
        "created_at",
    )
    list_filter = (
        "website",
        "event_type",
        "conversion_stage",
        "created_at",
    )
    search_fields = (
        "event_type",
        "special_order__title",
        "actor__email",
    )
    readonly_fields = (
        "metadata",
        "created_at",
        "updated_at",
    )
    raw_id_fields = (
        "special_order",
        "actor",
    )


@admin.register(SpecialOrderPlatformDifficultyRule)
class SpecialOrderPlatformDifficultyRuleAdmin(admin.ModelAdmin):
    list_display = (
        "predefined_order",
        "website",
        "platform",
        "difficulty_level",
        "multiplier",
        "is_active",
    )
    list_filter = (
        "website",
        "platform",
        "difficulty_level",
        "is_active",
    )
    search_fields = (
        "predefined_order__name",
        "platform",
    )
    raw_id_fields = (
        "predefined_order",
    )


@admin.register(SpecialOrderRushSurchargeRule)
class SpecialOrderRushSurchargeRuleAdmin(admin.ModelAdmin):
    list_display = (
        "predefined_order",
        "website",
        "max_duration_days",
        "surcharge_percentage",
        "is_active",
    )
    list_filter = (
        "website",
        "max_duration_days",
        "is_active",
    )
    search_fields = (
        "predefined_order__name",
    )
    raw_id_fields = (
        "predefined_order",
    )


@admin.register(SpecialOrderWriterLevelSurchargeRule)
class SpecialOrderWriterLevelSurchargeRuleAdmin(admin.ModelAdmin):
    list_display = (
        "predefined_order",
        "website",
        "writer_level",
        "surcharge_percentage",
        "is_active",
    )
    list_filter = (
        "website",
        "writer_level",
        "is_active",
    )
    search_fields = (
        "predefined_order__name",
    )
    raw_id_fields = (
        "predefined_order",
    )


@admin.register(SpecialOrderCurrencyPriceOverride)
class SpecialOrderCurrencyPriceOverrideAdmin(admin.ModelAdmin):
    list_display = (
        "duration",
        "website",
        "currency",
        "price",
        "is_active",
    )
    list_filter = (
        "website",
        "currency",
        "is_active",
    )
    search_fields = (
        "duration__predefined_order__name",
        "currency",
    )
    raw_id_fields = (
        "duration",
    )


@admin.register(SpecialOrderCapacityRule)
class SpecialOrderCapacityRuleAdmin(admin.ModelAdmin):
    list_display = (
        "predefined_order",
        "website",
        "duration_days",
        "max_active_orders",
        "is_active",
    )
    list_filter = (
        "website",
        "duration_days",
        "is_active",
    )
    search_fields = (
        "predefined_order__name",
    )
    raw_id_fields = (
        "predefined_order",
    )