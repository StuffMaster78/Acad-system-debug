from decimal import Decimal, ROUND_HALF_UP
from django.core.cache import cache
from django.utils.timezone import now

from models.payout import CurrencyConversionRate


class CurrencyConversionService:
    """Manages currency conversion rates and calculations."""

    CACHE_TIMEOUT_SECONDS = 60 * 60  # 1 hour

    @staticmethod
    def _cache_key(website_id, currency: str) -> str:
        return f"conversion_rate:{website_id}:{currency}"

    @staticmethod
    def validate_supported_currency(website, currency: str):
        """
        Raise error if currency is not supported for a given website.
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
        Get most recent conversion rate from USD to the given currency.
        Caches result in Redis (1 hour by default).
        """
        if on_date:
            # No caching if querying a historical rate
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

        # Try cache first
        cache_key = CurrencyConversionService._cache_key(
            website.id, target_currency
        )
        cached_rate = cache.get(cache_key)
        if cached_rate:
            return Decimal(str(cached_rate))

        # Fallback to DB
        rate_entry = CurrencyConversionRate.objects.filter(
            website=website,
            target_currency=target_currency
        ).order_by("-effective_date").first()

        if not rate_entry:
            raise ValueError(
                f"No current conversion rate for {target_currency} "
                f"on website {website}"
            )

        cache.set(
            cache_key,
            str(rate_entry.rate),  # store as string to avoid serialization issues
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

        Returns:
            tuple: (converted_amount, used_rate)
        """
        rate = CurrencyConversionService.get_latest_rate(
            website, target_currency
        )
        converted = (amount_usd * rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        return converted, rate

    @staticmethod
    def preview_all_rates(website):
        """
        Return a dict of all supported currencies with latest rates.
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