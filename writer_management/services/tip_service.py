from decimal import Decimal
from django.db import transaction
from writer_management.models import WriterLevel, Tip


class TipService:
    """
    Service for handling tips and their distribution between writers and the platform.

    """
    DEFAULT_WRITER_PERCENTAGE = Decimal("30.00")

    @classmethod
    def compute_split(cls, amount, writer_level=None):
        """
        Computes how much goes to the writer and how much to the platform.
        """
        if writer_level and writer_level.tip_percentage:
            pct = Decimal(writer_level.tip_percentage)
        else:
            pct = cls.DEFAULT_WRITER_PERCENTAGE

        writer_share = (amount * pct / Decimal("100.00")).quantize(Decimal("0.01"))
        platform_profit = (amount - writer_share).quantize(Decimal("0.01"))

        return pct, writer_share, platform_profit

    @classmethod
    @transaction.atomic
    def create_tip(
        cls, client, writer, order, amount,
        reason="", website=None, writer_level=None,
        related_entity_type=None, related_entity_id=None,
        origin="client"
    ):
        """
        Creates a tip and computes the split.
        """
        # Fallback to current writer level if not passed
        if writer_level is None and hasattr(writer, "level"):
            writer_level = writer.level

        pct, writer_earning, platform_profit = cls.compute_split(
            amount, writer_level
        )

        tip = Tip.objects.create(
            client=client,
            writer=writer,
            order=order,
            tip_amount=amount,
            tip_reason=reason,
            website=website,
            writer_level=writer_level,
            writer_percentage=pct,
            writer_earning=writer_earning,
            platform_profit=platform_profit,
            origin=origin,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
        )

        return tip