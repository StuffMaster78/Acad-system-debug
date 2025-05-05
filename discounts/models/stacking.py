from django.db import models
from .discount import Discount

class DiscountStackingRule(models.Model):
    """
    A model that links discounts that can be combined.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='discount_stacking_rule'
    )
    discount = models.ForeignKey(
        Discount,
        on_delete=models.CASCADE
    )
    stackable_discount = models.ForeignKey(
        Discount,
        related_name='stackable_discounts',
        on_delete=models.CASCADE
    )


    class Meta:
        unique_together = ("base_discount", "stackable_with")

    def __str__(self):
        return f"{self.base_discount.code} can stack with {self.stackable_with.code}"