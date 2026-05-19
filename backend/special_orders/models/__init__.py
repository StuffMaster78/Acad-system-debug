from django.conf import settings
from django.db import models

from websites.models.websites import Website

from special_orders.models.configs import (
    EstimatedSpecialOrderSettings,
    PredefinedSpecialOrderConfig,
    PredefinedSpecialOrderDuration,
    SpecialOrderMilestoneTemplate,
    SpecialOrderMilestoneTemplateItem,
    SpecialOrderWriterPayRule,
)
from special_orders.models.funding import (
    SpecialOrderFundingMilestone,
    SpecialOrderFundingPlan,
    SpecialOrderPaymentApplication,
    SpecialOrderRefundApplication,
)

InstallmentPayment = SpecialOrderFundingMilestone
from special_orders.models.pricing_snapshot import (
    SpecialOrderPricingSnapshot,
)
from special_orders.models.quotes import (
    SpecialOrderQuote,
    SpecialOrderQuoteLine,
)
from special_orders.models.special_order import (
    SpecialOrder,
    SpecialOrderStatusHistory,
)
from special_orders.models.discounts import (
    SpecialOrderDiscountApplication,
    SpecialOrderDiscountRule,
)
from special_orders.models.change_requests import (
    SpecialOrderChangeRequest,
    SpecialOrderChangeRequestQuote,
)
from special_orders.models.delivery import (
    SpecialOrderCompletionLog,
    SpecialOrderDeliverable,
    SpecialOrderDeliveryCheckpoint,
)
from special_orders.models.disputes import (
    SpecialOrderDispute,
    SpecialOrderDisputeResolution,
)
from special_orders.models.overrides import (
    SpecialOrderAdminOverride,
)
from special_orders.models.analytics import (
    SpecialOrderAnalyticsEvent,
)
from special_orders.models.sensitive_access import (
    SpecialOrderAccessGrant,
    SpecialOrderAccessLog,
    SpecialOrderExternalLink,
    SpecialOrderInstitutionProfile,
    SpecialOrderPlatformAccessVault,
    SpecialOrderTwoFactorRequest,
)


class WriterBonus(models.Model):
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_bonus",
    )
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "writer"},
    )
    special_order = models.ForeignKey(
        SpecialOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="special_order_bonuses",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(
        max_length=50,
        choices=[
            ("performance", "Outstanding Performance"),
            ("order_completion", "Order Completion"),
            ("client_tip", "Client Tip"),
            ("class_payment", "Class Payment"),
            ("other", "Other"),
        ],
        default="client_tip",
    )
    reason = models.TextField(blank=True)
    is_paid = models.BooleanField(default=False)
    granted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"Bonus of ${self.amount} to {self.writer} "
            f"(Category: {self.category})"
        )


class SpecialOrderInquiryFile(models.Model):
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="special_order_inquiry_files",
    )
    special_order = models.ForeignKey(
        SpecialOrder,
        on_delete=models.CASCADE,
        related_name="inquiry_files",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_special_order_inquiry_files",
    )
    file = models.FileField(upload_to="special_order_inquiries/")
    original_name = models.CharField(max_length=255, blank=True)
    content_type = models.CharField(max_length=120, blank=True)
    size = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)


__all__ = [
    "EstimatedSpecialOrderSettings",
    "InstallmentPayment",
    "PredefinedSpecialOrderConfig",
    "PredefinedSpecialOrderDuration",
    "SpecialOrder",
    "SpecialOrderFundingMilestone",
    "SpecialOrderFundingPlan",
    "SpecialOrderInquiryFile",
    "SpecialOrderMilestoneTemplate",
    "SpecialOrderMilestoneTemplateItem",
    "SpecialOrderPaymentApplication",
    "SpecialOrderPricingSnapshot",
    "SpecialOrderQuote",
    "SpecialOrderQuoteLine",
    "SpecialOrderRefundApplication",
    "SpecialOrderStatusHistory",
    "SpecialOrderWriterPayRule",
    "WriterBonus",
    "SpecialOrderDiscountApplication",
    "SpecialOrderDiscountRule",
    "SpecialOrderChangeRequest",
    "SpecialOrderChangeRequestQuote",
    "SpecialOrderCompletionLog",
    "SpecialOrderDeliverable",
    "SpecialOrderDeliveryCheckpoint",
    "SpecialOrderDispute",
    "SpecialOrderDisputeResolution",
    "SpecialOrderAdminOverride",
    "SpecialOrderAnalyticsEvent",
    "SpecialOrderAccessGrant",
    "SpecialOrderAccessLog",
    "SpecialOrderExternalLink",
    "SpecialOrderInstitutionProfile",
    "SpecialOrderPlatformAccessVault",
    "SpecialOrderTwoFactorRequest",
]
