from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand
from django.db.models import Q

from class_management.models import ClassOrder
from orders.models import Order
from orders.models.orders.order_number_sequence import OrderNumberScope
from orders.services.order_number_service import OrderNumberService
from special_orders.models import SpecialOrder


class Command(BaseCommand):
    help = "Backfill public order numbers for normal, class, and special orders."

    SCOPE_MODELS = {
        OrderNumberScope.NORMAL_ORDER: (Order, "public_order_number"),
        OrderNumberScope.CLASS_ORDER: (ClassOrder, "public_order_number"),
        OrderNumberScope.SPECIAL_ORDER: (SpecialOrder, "public_order_number"),
    }

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--scope",
            choices=["all", *self.SCOPE_MODELS.keys()],
            default="all",
            help="Which work type to backfill.",
        )
        parser.add_argument(
            "--period",
            default=None,
            help="Sequence period to use. Defaults to the current YYYY-MM.",
        )
        parser.add_argument(
            "--website-id",
            type=int,
            default=None,
            help="Limit to one website id.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would be stamped without saving.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        scopes = (
            list(self.SCOPE_MODELS.keys())
            if options["scope"] == "all"
            else [options["scope"]]
        )
        total_stamped = 0
        total_skipped = 0

        for scope in scopes:
            stamped, skipped = self._backfill_scope(
                scope=scope,
                period=options["period"],
                website_id=options["website_id"],
                dry_run=options["dry_run"],
            )
            total_stamped += stamped
            total_skipped += skipped

        verb = "Would stamp" if options["dry_run"] else "Stamped"
        self.stdout.write(
            self.style.SUCCESS(
                f"{verb} {total_stamped} records. Skipped {total_skipped} without active sequences."
            )
        )

    def _backfill_scope(
        self,
        *,
        scope: str,
        period: str | None,
        website_id: int | None,
        dry_run: bool,
    ) -> tuple[int, int]:
        model, field_name = self.SCOPE_MODELS[scope]
        qs = model.objects.filter(
            Q(**{f"{field_name}__isnull": True}) | Q(**{field_name: ""})
        )
        if website_id is not None:
            qs = qs.filter(website_id=website_id)

        stamped = 0
        skipped = 0

        for instance in qs.select_related("website").iterator():
            number = OrderNumberService.build_reference_for_id(
                website=instance.website,
                object_id=instance.pk,
                scope=scope,
                period=period,
            )
            if number is None:
                skipped += 1
                continue

            stamped += 1
            self.stdout.write(
                f"{scope}: {instance.pk} -> {number}"
                + (" (dry run)" if dry_run else "")
            )
            if dry_run:
                continue

            setattr(instance, field_name, number)
            update_fields = [field_name]
            if hasattr(instance, "updated_at"):
                update_fields.append("updated_at")
            instance.save(update_fields=update_fields)

        return stamped, skipped
