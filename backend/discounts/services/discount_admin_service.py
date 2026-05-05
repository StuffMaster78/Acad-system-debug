from __future__ import annotations

from decimal import Decimal
from typing import Iterable

from django.db import transaction
from django.utils import timezone

from discounts.constants import DiscountOrigin
from discounts.constants import DiscountType
from discounts.exceptions import DiscountConfigurationError
from discounts.models.discount import Discount
from discounts.services.discount_code_generator import (
    DiscountCodeGenerator,
)
from discounts.validators.code_format_validator import (
    DiscountCodeFormatValidator,
)


class DiscountAdminService:
    """
    Admin write operations for discounts.
    """

    @staticmethod
    @transaction.atomic
    def create_discount(
        *,
        website,
        name: str,
        discount_code: str,
        discount_type: str,
        discount_value: Decimal,
        created_by=None,
        description: str = "",
        campaign=None,
        max_discount_amount: Decimal | None = None,
        min_payable_amount: Decimal = Decimal("0.00"),
        starts_at=None,
        ends_at=None,
        usage_limit: int | None = None,
        per_client_usage_limit: int | None = None,
        first_order_only: bool = False,
        eligible_clients: Iterable | None = None,
        origin: str = DiscountOrigin.MANUAL,
        is_active: bool = True,
        is_campaign_managed: bool = True,
    ) -> Discount:
        """
        Create a tenant scoped discount.
        """
        DiscountAdminService._validate_website(website=website)
        DiscountAdminService._validate_campaign(
            website=website,
            campaign=campaign,
        )
        DiscountAdminService._validate_discount_values(
            discount_type=discount_type,
            discount_value=discount_value,
            max_discount_amount=max_discount_amount,
            min_payable_amount=min_payable_amount,
        )
        DiscountAdminService._validate_usage_limits(
            usage_limit=usage_limit,
            per_client_usage_limit=per_client_usage_limit,
        )

        normalized_code = DiscountCodeGenerator.normalize(discount_code)
        DiscountCodeFormatValidator()(normalized_code)

        discount = Discount.objects.create(
            website=website,
            campaign=campaign,
            discount_code=normalized_code,
            name=name,
            description=description,
            discount_type=discount_type,
            discount_value=discount_value,
            max_discount_amount=max_discount_amount,
            min_payable_amount=min_payable_amount,
            starts_at=starts_at,
            ends_at=ends_at,
            usage_limit=usage_limit,
            per_client_usage_limit=per_client_usage_limit,
            first_order_only=first_order_only,
            origin=origin,
            is_active=is_active,
            is_campaign_managed=is_campaign_managed,
            created_by=created_by,
            updated_by=created_by,
        )

        if eligible_clients:
            clients = DiscountAdminService._filter_tenant_clients(
                website=website,
                eligible_clients=eligible_clients,
            )
            discount.eligible_clients.set(clients)

        return discount

    @staticmethod
    @transaction.atomic
    def create_holiday_discount(
        *,
        website,
        name: str,
        discount_type: str,
        discount_value: Decimal,
        created_by=None,
        discount_code: str | None = None,
        starts_at=None,
        ends_at=None,
        campaign=None,
    ) -> Discount:
        """
        Create a holiday originated discount.
        """
        code = discount_code or DiscountCodeGenerator.generate(
            prefix="HOLIDAY",
        )

        return DiscountAdminService.create_discount(
            website=website,
            name=name,
            discount_code=code,
            discount_type=discount_type,
            discount_value=discount_value,
            starts_at=starts_at,
            ends_at=ends_at,
            campaign=campaign,
            per_client_usage_limit=1,
            origin=DiscountOrigin.HOLIDAY,
            created_by=created_by,
        )

    @staticmethod
    @transaction.atomic
    def create_loyalty_discount(
        *,
        website,
        client,
        discount_type: str,
        discount_value: Decimal,
        created_by=None,
        max_discount_amount: Decimal | None = None,
        expires_at=None,
    ) -> Discount:
        """
        Create a one use loyalty reward discount for a client.
        """
        DiscountAdminService._validate_client_tenant(
            website=website,
            client=client,
        )

        discount = DiscountAdminService.create_discount(
            website=website,
            name="Loyalty reward discount",
            discount_code=DiscountCodeGenerator.generate(
                prefix="LOYALTY",
            ),
            discount_type=discount_type,
            discount_value=discount_value,
            max_discount_amount=max_discount_amount,
            ends_at=expires_at,
            usage_limit=1,
            per_client_usage_limit=1,
            origin=DiscountOrigin.LOYALTY,
            created_by=created_by,
        )
        discount.eligible_clients.set([client])

        return discount

    @staticmethod
    @transaction.atomic
    def get_or_create_first_order_discount(
        *,
        website,
        config,
        created_by=None,
    ) -> Discount:
        """
        Return the tenant system discount for first order purchases.
        """
        DiscountAdminService._validate_website(website=website)

        discount, created = Discount.objects.get_or_create(
            website=website,
            discount_code="FIRSTORDER",
            defaults={
                "name": "First order discount",
                "description": "Automatic first order client discount.",
                "discount_type": config.discount_type,
                "discount_value": config.discount_value,
                "max_discount_amount": config.max_discount_amount,
                "min_payable_amount": config.min_payable_amount,
                "usage_limit": None,
                "per_client_usage_limit": 1,
                "first_order_only": True,
                "origin": DiscountOrigin.FIRST_ORDER,
                "is_active": config.is_enabled,
                "created_by": created_by,
                "updated_by": created_by,
            },
        )

        if not created:
            discount.discount_type = config.discount_type
            discount.discount_value = config.discount_value
            discount.max_discount_amount = config.max_discount_amount
            discount.min_payable_amount = config.min_payable_amount
            discount.is_active = config.is_enabled
            discount.updated_by = created_by
            discount.save(
                update_fields=[
                    "discount_type",
                    "discount_value",
                    "max_discount_amount",
                    "min_payable_amount",
                    "is_active",
                    "updated_by",
                    "updated_at",
                ]
            )

        return discount

    @staticmethod
    @transaction.atomic
    def update_discount(
        *,
        discount: Discount,
        updated_by=None,
        eligible_clients=None,
        **fields,
    ) -> Discount:
        """
        Update a discount safely through the service layer.
        """
        allowed_fields = {
            "campaign",
            "discount_code",
            "name",
            "description",
            "discount_type",
            "discount_value",
            "max_discount_amount",
            "min_payable_amount",
            "starts_at",
            "ends_at",
            "usage_limit",
            "per_client_usage_limit",
            "first_order_only",
            "origin",
            "is_active",
            "is_campaign_managed",
        }

        unknown_fields = set(fields) - allowed_fields

        if unknown_fields:
            raise DiscountConfigurationError(
                "Unsupported discount update fields: "
                f"{', '.join(sorted(unknown_fields))}"
            )

        website = discount.website

        DiscountAdminService._validate_website(website=website)

        campaign = fields.get("campaign", discount.campaign)
        DiscountAdminService._validate_campaign(
            website=website,
            campaign=campaign,
        )

        starts_at = fields.get("starts_at", discount.starts_at)
        ends_at = fields.get("ends_at", discount.ends_at)
        DiscountAdminService._validate_date_window(
            starts_at=starts_at,
            ends_at=ends_at,
        )

        discount_type = fields.get(
            "discount_type",
            discount.discount_type,
        )
        discount_value = fields.get(
            "discount_value",
            discount.discount_value,
        )
        max_discount_amount = fields.get(
            "max_discount_amount",
            discount.max_discount_amount,
        )
        min_payable_amount = fields.get(
            "min_payable_amount",
            discount.min_payable_amount,
        )

        DiscountAdminService._validate_discount_values(
            discount_type=discount_type,
            discount_value=discount_value,
            max_discount_amount=max_discount_amount,
            min_payable_amount=min_payable_amount,
        )

        usage_limit = fields.get("usage_limit", discount.usage_limit)
        per_client_usage_limit = fields.get(
            "per_client_usage_limit",
            discount.per_client_usage_limit,
        )

        DiscountAdminService._validate_usage_limits(
            usage_limit=usage_limit,
            per_client_usage_limit=per_client_usage_limit,
        )

        if "discount_code" in fields:
            normalized_code = DiscountCodeGenerator.normalize(
                fields["discount_code"],
            )
            DiscountAdminService._validate_unique_code(
                website=website,
                discount_code=normalized_code,
                current_discount_id=discount.pk,
            )
            fields["discount_code"] = normalized_code

        for field, value in fields.items():
            setattr(discount, field, value)

        discount.updated_by = updated_by
        discount.save()

        if eligible_clients is not None:
            clients = DiscountAdminService._filter_tenant_clients(
                website=website,
                eligible_clients=eligible_clients,
            )
            discount.eligible_clients.set(clients)

        return discount


    @staticmethod
    @transaction.atomic
    def archive_discount(*, discount, updated_by=None) -> Discount:
        """
        Archive a discount without deleting usage history.
        """
        discount.is_archived = True
        discount.updated_by = updated_by
        discount.save(
            update_fields=[
                "is_archived",
                "updated_by",
                "updated_at",
            ]
        )

        return discount

    @staticmethod
    @transaction.atomic
    def restore_discount(*, discount, updated_by=None) -> Discount:
        """
        Restore an archived discount.
        """
        discount.is_archived = False
        discount.updated_by = updated_by
        discount.save(
            update_fields=[
                "is_archived",
                "updated_by",
                "updated_at",
            ]
        )

        return discount

    @staticmethod
    def _validate_website(*, website) -> None:
        """
        Ensure a tenant website is present.
        """
        if not website or not getattr(website, "id", None):
            raise DiscountConfigurationError(
                "A valid website is required."
            )

    @staticmethod
    def _validate_campaign(*, website, campaign) -> None:
        """
        Ensure campaign belongs to the same tenant.
        """
        if campaign is None:
            return

        if campaign.website_id != website.id:
            raise DiscountConfigurationError(
                "Campaign does not belong to this website."
            )

    @staticmethod
    def _validate_client_tenant(*, website, client) -> None:
        """
        Ensure the client belongs to the same tenant.
        """
        if getattr(client, "website_id", None) != website.id:
            raise DiscountConfigurationError(
                "Client does not belong to this website."
            )

    @staticmethod
    def _validate_discount_values(
        *,
        discount_type: str,
        discount_value: Decimal,
        max_discount_amount: Decimal | None,
        min_payable_amount: Decimal,
    ) -> None:
        """
        Validate discount numeric values.
        """
        if discount_type not in {
            DiscountType.PERCENTAGE,
            DiscountType.FIXED_AMOUNT,
        }:
            raise DiscountConfigurationError(
                "Unsupported discount type."
            )

        if discount_value <= Decimal("0.00"):
            raise DiscountConfigurationError(
                "Discount value must be greater than zero."
            )

        if (
            discount_type == DiscountType.PERCENTAGE
            and discount_value > Decimal("100.00")
        ):
            raise DiscountConfigurationError(
                "Percentage discount cannot exceed 100."
            )

        if (
            max_discount_amount is not None
            and max_discount_amount < Decimal("0.00")
        ):
            raise DiscountConfigurationError(
                "Maximum discount amount cannot be negative."
            )

        if min_payable_amount < Decimal("0.00"):
            raise DiscountConfigurationError(
                "Minimum payable amount cannot be negative."
            )

    @staticmethod
    def _validate_usage_limits(
        *,
        usage_limit: int | None,
        per_client_usage_limit: int | None,
    ) -> None:
        """
        Validate global and per client usage limits.
        """
        if usage_limit is not None and usage_limit < 1:
            raise DiscountConfigurationError(
                "Usage limit must be greater than zero."
            )

        if (
            per_client_usage_limit is not None
            and per_client_usage_limit < 1
        ):
            raise DiscountConfigurationError(
                "Per client usage limit must be greater than zero."
            )

        if (
            usage_limit is not None
            and per_client_usage_limit is not None
            and per_client_usage_limit > usage_limit
        ):
            raise DiscountConfigurationError(
                "Per client usage limit cannot exceed usage limit."
            )

    @staticmethod
    def _filter_tenant_clients(*, website, eligible_clients):
        """
        Keep only clients belonging to the discount website.
        """
        return [
            client
            for client in eligible_clients
            if getattr(client, "website_id", None) == website.id
        ]
    
    @staticmethod
    def _validate_unique_code(
        *,
        website,
        discount_code: str,
        current_discount_id: int | None = None,
    ) -> None:
        """
        Ensure discount code is unique within a website.
        """
        queryset = Discount.objects.filter(
            website=website,
            discount_code=discount_code,
        )

        if current_discount_id is not None:
            queryset = queryset.exclude(id=current_discount_id)

        if queryset.exists():
            raise DiscountConfigurationError(
                "A discount with this code already exists."
            )


    @staticmethod
    def _validate_date_window(
        *,
        starts_at=None,
        ends_at=None,
    ) -> None:
        """
        Validate discount or campaign date window.
        """
        now = timezone.now()

        if starts_at and ends_at and starts_at >= ends_at:
            raise DiscountConfigurationError(
                "Start date must be earlier than end date."
            )

        if ends_at and ends_at <= now:
            raise DiscountConfigurationError(
                "End date must be in the future."
            )