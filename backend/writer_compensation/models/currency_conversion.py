"""
Currency conversion rates for multi-currency payouts.

Stores USD → target currency rates effective on a given date.
Used by payout system to convert writer compensation amounts.
"""

from django.db import models


class CurrencyConversionRate(models.Model):
    """
    Stores conversion rates from USD to other currencies.

    One row per (website, currency, effective_date) tuple.
    Read by payout services to determine conversion at payment time.

    Example:
        website=acme.com, target_currency=KSH, effective_date=2025-05-01
        1 USD = 123.45 KSH
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="conversion_rates"
    )
    target_currency = models.CharField(
        max_length=10,
        default="KSH",
        help_text="The currency to convert to (e.g., KSH)."
    )
    rate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        help_text="Conversion rate from 1 USD to target currency."
    )
    effective_date = models.DateField(
        help_text="The date this rate became effective."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Currency Conversion Rate"
        verbose_name_plural = "Currency Conversion Rates"
        unique_together = ("website", "target_currency", "effective_date")
        indexes = [
            models.Index(fields=["website", "target_currency", "-effective_date"]),
        ]

    def __str__(self):
        return (
            f"{self.target_currency} @ {self.rate} "
            f"(as of {self.effective_date})"
        )
