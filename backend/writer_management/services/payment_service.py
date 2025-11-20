from decimal import Decimal
from django.utils.timezone import now
from django.core.exceptions import PermissionDenied
from audit_logging.services.audit_log_service import (
    AuditLogService as AuditLogger
)
from writer_management.models.profile import WriterProfile
from websites.models import Website
from writer_management.models.payout import WriterPayment
from writer_management.services.conversion_service import (
    CurrencyConversionService
)


class WriterPaymentService:
    @staticmethod
    def create_payment(
        *,
        writer: WriterProfile,
        website: Website,
        amount_usd: Decimal,
        bonuses: Decimal = Decimal("0.00"),
        fines: Decimal = Decimal("0.00"),
        tips: Decimal = Decimal("0.00"),
        currency: str = "USD",
        convert_to_local: bool = False,
        description: str = "",
        payment_date=None,
        actor=None  # Optional: track who created it
    ) -> WriterPayment:
        """
        Creates a writer payment entry, optionally converting to a local currency.
        """

        if convert_to_local:
            if currency == "USD":
                raise ValueError("No need to convert to USD.")

            # Only allow admin to perform conversions
            if actor and not actor.is_staff:
                raise PermissionDenied("Only admins can convert currency.")

            converted_amount, rate = CurrencyConversionService.convert_usd_to_local(
                amount_usd, website, target_currency=currency
            )
            currency_used = currency
        else:
            converted_amount = amount_usd
            rate = Decimal("1.00")
            currency_used = "USD"

        total = (converted_amount + bonuses + tips - fines).quantize(Decimal("0.01"))

        AuditLogger.log_auto(
            action="create_payment",
            actor=actor,
            target=writer,
            metadata={
                "website": website.id,
                "writer": writer.id,
                "amount_usd": str(amount_usd),
                "bonuses": str(bonuses),
                "fines": str(fines),
                "tips": str(tips),
                "currency": currency_used,
                "converted_amount": str(converted_amount),
                "conversion_rate": str(rate),
                "payment_date": payment_date or now(),
            },
            notes=description or f"Payout in {currency_used} on {now().date()}",
        )


        return WriterPayment.objects.create(
            writer=writer,
            website=website,
            amount=total,
            bonuses=bonuses,
            fines=fines,
            tips=tips,
            converted_amount=converted_amount,
            conversion_rate=rate,
            currency=currency_used,
            payment_date=payment_date or now(),
            description=description or f"Payout in {currency_used} on {now().date()}",
        )