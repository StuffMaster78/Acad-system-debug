"""
Currency conversion service for multi-currency payouts.

Converts USD → local currency (e.g., KSH) using effective-date rates.
Caches rates in Redis to avoid repeated DB queries.

FLOW:
  1. Writer earns $100 USD
  2. Service gets latest KSH rate: 1 USD = 123.45 KSH
  3. Calculates: 100 × 123.45 = 12,345.00 KSH
  4. Stores conversion rate with payment for audit trail
"""

from decimal import Decimal, ROUND_HALF_UP
from django.core.cache import cache
from writer_compensation.models.currency_conversion import CurrencyConversionRate


class CurrencyConversionService:
    """
    Manages currency conversion rates and calculations.

    USAGE:
        # Validate currency is supported
        CurrencyConversionService.validate_supported_currency(website, "KSH")

        # Convert USD to KSH
        converted_amount, rate_used = CurrencyConversionService.convert_usd_to_local(
            amount_usd=Decimal("100.00"),
            website=website,
            target_currency="KSH"
        )

        # Get rate as of specific date (for historical audits)
        rate = CurrencyConversionService.get_latest_rate(
            website=website,
            target_currency="KSH",
            on_date=datetime(2025, 01, 01).date()
        )

        # See all rates for a website
        all_rates = CurrencyConversionService.preview_all_rates(website)
    """

    CACHE_TIMEOUT_SECONDS = 60 * 60  # 1 hour

    @staticmethod
    def _cache_key(website_id, currency: str) -> str:
        """Generate Redis cache key for a conversion rate."""
        return f"conversion_rate:{website_id}:{currency}"

    @staticmethod
    def validate_supported_currency(website, currency: str):
        """
        Raise error if currency is not supported for a given website.

        Checks if at least one rate entry exists for the currency.
        """
        exists = CurrencyConversionRate.objects.filter(
            website=website,
            target_currency=currency
        ).exists()
        if not exists:
            raise ValueError(
                f"Currency '{currency}' not supported for {website}"
            )

    @staticmethod
    def get_latest_rate(
        website, target_currency="KSH", on_date=None
    ) -> Decimal:
        """
        Get conversion rate (1 USD → target_currency).

        Args:
            website: Site to get rates for
            target_currency: e.g. "KSH", "NGN"
            on_date: If provided, get rate effective on that date (no caching)
                     If None, get current rate (with 1hr Redis cache)

        Returns:
            Decimal: The conversion rate

        Raises:
            ValueError: If no rate found for currency/date combination
        """
        if on_date:
            # Historical query — no caching
            # Find most recent rate on or before the given date
            qs = CurrencyConversionRate.objects.filter(
                website=website,
                target_currency=target_currency,
                effective_date__lte=on_date
            )
            rate_entry = qs.order_by("-effective_date").first()
            if not rate_entry:
                raise ValueError(
                    f"No rate found for {target_currency} at {website} "
                    f"(on_date={on_date})"
                )
            return rate_entry.rate

        # Current rate — use cache
        cache_key = CurrencyConversionService._cache_key(
            website.id, target_currency
        )
        cached_rate = cache.get(cache_key)
        if cached_rate:
            return Decimal(str(cached_rate))

        # Cache miss — fetch from DB
        rate_entry = CurrencyConversionRate.objects.filter(
            website=website,
            target_currency=target_currency
        ).order_by("-effective_date").first()

        if not rate_entry:
            raise ValueError(
                f"No current conversion rate for {target_currency} "
                f"on website {website}"
            )

        # Store as string to avoid Decimal serialization issues in Redis
        cache.set(
            cache_key,
            str(rate_entry.rate),
            timeout=CurrencyConversionService.CACHE_TIMEOUT_SECONDS
        )
        return rate_entry.rate

    @staticmethod
    def convert_usd_to_local(
        amount_usd: Decimal,
        website,
        target_currency="KSH"
    ) -> tuple[Decimal, Decimal]:
        """
        Convert USD amount to local currency using latest rate.

        Performs rounding to 2 decimal places (standard for currency).

        Args:
            amount_usd: Amount in USD (e.g., Decimal("100.00"))
            website: Site to get rates for
            target_currency: e.g. "KSH", "NGN"

        Returns:
            tuple: (converted_amount, rate_used)
            Example: (Decimal("12345.00"), Decimal("123.45"))
        """
        rate = CurrencyConversionService.get_latest_rate(
            website, target_currency
        )
        # Multiply: 100 USD × 123.45 = 12345.00
        converted = (amount_usd * rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        return converted, rate

    @staticmethod
    def preview_all_rates(website):
        """
        Return dict of all supported currencies with latest rates.

        Returns:
            dict: {
                "KSH": Decimal("123.45"),
                "NGN": Decimal("1500.00"),
                ...
            }
        """
        latest_rates = (
            CurrencyConversionRate.objects.filter(website=website)
            .order_by("target_currency", "-effective_date")
            .distinct("target_currency")
        )
        return {
            entry.target_currency: entry.rate
            for entry in latest_rates
        }

    @staticmethod
    def clear_rate_cache(website_id, currency: str):
        """
        Manually clear cached rate (called when new rate is added).

        Fired by Django signal when CurrencyConversionRate is saved.
        """
        cache_key = CurrencyConversionService._cache_key(website_id, currency)
        cache.delete(cache_key)
