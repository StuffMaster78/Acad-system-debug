"""
Model for storing website-specific discount configuration settings.
"""

from django.db import models


class DiscountConfig(models.Model):
    """
    Stores configurable discount settings for each website, such as how many
    discount codes can be stacked, the minimum threshold for stacking, and
    the maximum allowed discount percentage.
    """

    website = models.OneToOneField(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="discount_config",
        help_text="The website this configuration applies to."
    )

    max_stackable_discounts = models.PositiveIntegerField(
        default=1,
        help_text=(
            "Maximum number of discount codes that can be applied to a "
            "single order."
        )
    )
    enable_stacking = models.BooleanField(default=True)
    enable_hints = models.BooleanField(default=True)
    discount_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=100.00,
        help_text=(
            "Minimum order total required (after applying the first discount) "
            "to allow stacking additional discounts."
        )
    )

    max_discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=30.00,
        help_text="Maximum total discount percent allowed per order."
    )

    allow_stack_across_events = models.BooleanField(
        default=False,
        help_text=(
            "Allow stacking discount codes from different promotional campaigns "
            "on the same order."
        )
    )
    promotional_campaign_discount_active = models.BooleanField(
        default=True, help_text="Is the promotional campaign discount active?"
    )
    promotional_campaign_discount_value = models.DecimalField(
        default=10.00, max_digits=5, decimal_places=2,
        help_text="Value of promotional campaign discount in percentage"
    )
    promotional_campaign = models.ForeignKey(
        "discounts.PromotionalCampaign",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="The promotional campaign linked to this discount"
    )

    created_by = models.ForeignKey(
        "users.User", 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        help_text="User who created or last updated the discount config"
    )
    updated_by = models.ForeignKey(
        "users.User", 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name="discount_configs_updated",
        help_text="User who last updated the discount config"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        help_text="Timestamp when the discount config was created"
    )   
    updated_at = models.DateTimeField(
        auto_now=True, 
        help_text="Timestamp of the last update"
    )


    class Meta:
        verbose_name = "Discount Configuration"
        verbose_name_plural = "Discount Configurations"

    def __str__(self):
        return f"Discount Config for {self.website.name}"