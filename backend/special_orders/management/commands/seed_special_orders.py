from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from special_orders.models import (
    EstimatedSpecialOrderSettings,
    PredefinedSpecialOrderConfig,
    PredefinedSpecialOrderDuration,
    SpecialOrder,
)
from special_orders.services.new_services import (
    special_order_creation_service,
)
from websites.models.websites import Website


class Command(BaseCommand):
    """
    Seed fixed and quoted special-order configuration.
    """

    help = "Seed special order configurations and optional sample orders."

    def add_arguments(self, parser):
        parser.add_argument(
            "--website-id",
            type=int,
            help="Specific website ID to seed.",
        )
        parser.add_argument(
            "--create-orders",
            action="store_true",
            help="Also create sample special orders.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing special-order configs before seeding.",
        )

    def handle(self, *args, **options):
        websites = self._get_websites(
            website_id=options.get("website_id"),
        )
        if not websites.exists():
            self.stdout.write(self.style.WARNING("No websites found."))
            return

        with transaction.atomic():
            if options.get("clear"):
                self._clear_seed_data()

            total_configs = 0
            total_durations = 0

            for website in websites:
                counts = self._seed_website(website=website)
                total_configs += counts["configs"]
                total_durations += counts["durations"]

            if options.get("create_orders"):
                self._create_sample_orders(websites=websites)

        self.stdout.write(
            self.style.SUCCESS(
                "Seeded special orders: "
                f"{total_configs} configs, {total_durations} durations."
            )
        )

    def _get_websites(self, *, website_id: int | None):
        """
        Return websites targeted by the seed operation.
        """
        if website_id:
            return Website.objects.filter(id=website_id)

        queryset = Website.objects.all()
        if hasattr(Website, "is_active"):
            queryset = queryset.filter(is_active=True)

        return queryset

    def _clear_seed_data(self) -> None:
        """
        Clear seed-owned special-order data.
        """
        SpecialOrder.objects.all().delete()
        PredefinedSpecialOrderDuration.objects.all().delete()
        PredefinedSpecialOrderConfig.objects.all().delete()
        EstimatedSpecialOrderSettings.objects.all().delete()
        message = "Cleared special-order seed data."
        self.stdout.write(self.style.WARNING(message))

    def _seed_website(self, *, website) -> dict[str, int]:
        """
        Seed one website's special-order config.
        """
        self.stdout.write(f"Processing website: {website.name}")

        EstimatedSpecialOrderSettings.objects.get_or_create(
            website=website,
            defaults={
                "default_deposit_percentage": Decimal("50.00"),
                "minimum_deposit_amount": Decimal("0.00"),
                "allow_installments": True,
            },
        )

        total_configs = 0
        total_durations = 0

        for config_data in self._config_seed_data():
            config, created = (
                PredefinedSpecialOrderConfig.objects.update_or_create(
                    website=website,
                    slug=slugify(config_data["name"]),
                    defaults={
                        "name": config_data["name"],
                        "description": config_data["description"],
                        "is_active": True,
                        "requires_full_payment": True,
                        "allow_wallet_payment": True,
                        "allow_external_payment": True,
                        "allow_discounts": True,
                    },
                )
            )
            if created:
                total_configs += 1

            for duration_data in config_data["durations"]:
                _, duration_created = (
                    PredefinedSpecialOrderDuration.objects.update_or_create(
                        website=website,
                        predefined_order=config,
                        duration_days=duration_data["days"],
                        defaults={
                            "price": duration_data["price"],
                            "is_active": True,
                        },
                    )
                )
                if duration_created:
                    total_durations += 1

        return {
            "configs": total_configs,
            "durations": total_durations,
        }

    def _create_sample_orders(self, *, websites) -> None:
        """
        Create sample fixed and quoted special orders.
        """
        user_model = get_user_model()
        clients = list(
            user_model.objects.filter(role="client", is_active=True)[:5],
        )
        if not clients:
            self.stdout.write(
                self.style.WARNING("No active clients found."),
            )
            return

        total_orders = 0

        for website in websites:
            configs = PredefinedSpecialOrderConfig.objects.filter(
                website=website,
                is_active=True,
            ).prefetch_related("durations")[:3]

            for index, config in enumerate(configs):
                duration = config.durations.filter(is_active=True).first()
                if duration is None:
                    continue

                (
                    special_order_creation_service
                    .SpecialOrderCreationService
                    .create_fixed_order
                )(
                    website=website,
                    client=clients[index % len(clients)],
                    predefined_config=config,
                    predefined_duration=duration,
                    created_by=clients[index % len(clients)],
                )
                total_orders += 1

            (
                special_order_creation_service
                .SpecialOrderCreationService
                .create_quoted_order
            )(
                website=website,
                client=clients[0],
                title="Sample custom special order",
                inquiry_details="Sample quoted special-order request.",
                budget=Decimal("500.00"),
                duration_days=5,
                created_by=clients[0],
            )
            total_orders += 1

        self.stdout.write(
            self.style.SUCCESS(f"Created {total_orders} sample orders."),
        )

    @staticmethod
    def _config_seed_data() -> list[dict]:
        """
        Return default fixed special-order packages.
        """
        return [
            {
                "name": "Shadow Health",
                "description": "Shadow Health assignments and assessments.",
                "durations": [
                    {"days": 2, "price": Decimal("250.00")},
                    {"days": 3, "price": Decimal("350.00")},
                    {"days": 5, "price": Decimal("500.00")},
                ],
            },
            {
                "name": "ATI Comprehensive",
                "description": "ATI assessments and practice tests.",
                "durations": [
                    {"days": 2, "price": Decimal("200.00")},
                    {"days": 3, "price": Decimal("280.00")},
                    {"days": 5, "price": Decimal("400.00")},
                ],
            },
            {
                "name": "Custom Project",
                "description": "Custom special-order projects.",
                "durations": [
                    {"days": 2, "price": Decimal("180.00")},
                    {"days": 3, "price": Decimal("250.00")},
                    {"days": 5, "price": Decimal("380.00")},
                ],
            },
        ]
