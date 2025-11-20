from django.db import models
from django.core.exceptions import ValidationError

class DiscountStackingRule(models.Model):
    """
    Links discounts that can be combined in the system.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='discount_stacking_rules',
        help_text="The website for which this discount stacking rule applies"
    )
    base_discount = models.ForeignKey(
        'discounts.Discount',
        on_delete=models.CASCADE,
        related_name='base_discounts',
        help_text="The base discount that can be stacked"
    )
    stackable_with = models.ForeignKey(
        'discounts.Discount',
        related_name='stackable_discounts',
        on_delete=models.CASCADE,
        help_text="The discount that can be stacked on top of the base discount"
    )
    priority = models.PositiveIntegerField(
        default=0,
        help_text="Priority of this discount stack (lower number = higher priority)"
    )

    class Meta:
        ordering = ['priority']
        verbose_name = "Discount Stacking Rule"
        verbose_name_plural = "Discount Stacking Rules"
        constraints = [
            models.UniqueConstraint(
                fields=['base_discount', 'stackable_with'],
                name='unique_discount_stacking'
            )
        ]

    def clean(self):
        """
        Ensure base and stackable discounts are from same website and match rule.
        """
        if self.base_discount.website != self.stackable_with.website:
            raise ValidationError("Discounts must belong to the same website.")
        if self.website != self.base_discount.website:
            raise ValidationError("Stacking rule website must match discounts' website.")

    def __str__(self):
        return f"{self.base_discount.code} + {self.stackable_with.code} (priority {self.priority})"