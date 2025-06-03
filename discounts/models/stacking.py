from django.db import models
from .discount import Discount
from django.core.exceptions import ValidationError
class DiscountStackingRule(models.Model):
    """
    Links discounts that can be combined in the system.
    This model specifies which discounts can stack with each other, 
    and the priority order for stacking.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='discount_stacking_rule',
        help_text="The website for which this discount stacking rule applies"
    )
    discount = models.ForeignKey(
        Discount,
        on_delete=models.CASCADE,
        related_name='base_discounts',
        help_text="The base discount that can be stacked"
    )
    stackable_discount = models.ForeignKey(
        Discount,
        related_name='stackable_discounts',
        on_delete=models.CASCADE,
        help_text="The discount that can be stacked on top of the base discount"
    )
    priority = models.PositiveIntegerField(
        default=0,
        help_text="Priority of this discount stack (lower number = higher priority)"
    )

    class Meta:
        unique_together = ("discount", "stackable_discount")
        ordering = ['priority']
        verbose_name = "Discount Stacking Rule"
        verbose_name_plural = "Discount Stacking Rules"

    def clean(self):
        """
        Custom validation to ensure that the discounts and website are valid.
        """
        if self.discount.website != self.stackable_discount.website:
            raise ValidationError("Discounts must belong to the same website.")
        if self.discount.website != self.website:
            raise ValidationError("Stacking rule website must match discounts' website.")

    def __str__(self):
        return f"{self.discount.code} can stack with {self.stackable_discount.code} (priority {self.priority})"
