from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.utils import timezone

from orders.selectors.order_creation_selectors import (
    OrderCreationContext,
)


class OrderCreationValidator:
    """
    Enforce business rules for order creation.

    Responsibilities:
        1. Validate deadline relationships.
        2. Validate follow-up requirements.
        3. Validate unpaid access restrictions.
        4. Validate tenant-sensitive relationships like preferred writer.
        5. Validate that selected pricing snapshot matches request intent.

    This validator performs no writes and creates no side effects.
    """

    @classmethod
    def validate(
        cls,
        *,
        attrs: dict[str, Any],
        context: OrderCreationContext,
        request_user: Any,
    ) -> None:
        """
        Validate order creation business rules.

        Args:
            attrs:
                Incoming normalized request data.
            context:
                Resolved creation context.
            request_user:
                Current authenticated user.

        Raises:
            ValidationError:
                Raised when a business rule is violated.
        """
        cls._validate_deadlines(attrs=attrs)
        cls._validate_follow_up(attrs=attrs, context=context)
        cls._validate_unpaid_access(
            attrs=attrs,
            request_user=request_user,
        )
        cls._validate_preferred_writer_tenant(
            context=context,
            request_user=request_user,
        )
        cls._validate_previous_order_tenant(
            context=context,
            request_user=request_user,
        )
        cls._validate_pricing_snapshot_matches_request(
            attrs=attrs,
            context=context,
        )

    @staticmethod
    def _validate_deadlines(*, attrs: dict[str, Any]) -> None:
        """
        Validate client and writer deadlines.

        Args:
            attrs:
                Incoming normalized request data.

        Raises:
            ValidationError:
                Raised when deadline rules fail.
        """
        client_deadline = attrs["client_deadline"]
        writer_deadline = attrs.get("writer_deadline")

        if client_deadline <= timezone.now():
            raise ValidationError(
                {
                    "client_deadline": (
                        "client_deadline must be in the future."
                    )
                }
            )

        if (
            writer_deadline is not None
            and writer_deadline >= client_deadline
        ):
            raise ValidationError(
                {
                    "writer_deadline": (
                        "writer_deadline must be earlier than "
                        "client_deadline."
                    )
                }
            )

    @staticmethod
    def _validate_follow_up(
        *,
        attrs: dict[str, Any],
        context: OrderCreationContext,
    ) -> None:
        """
        Validate follow-up order requirements.

        Args:
            attrs:
                Incoming normalized request data.
            context:
                Resolved creation context.

        Raises:
            ValidationError:
                Raised when follow-up rules fail.
        """
        is_follow_up = attrs.get("is_follow_up", False)

        if is_follow_up and context.previous_order is None:
            raise ValidationError(
                {
                    "previous_order_id": (
                        "previous_order_id is required when "
                        "is_follow_up is True."
                    )
                }
            )

        if not is_follow_up and context.previous_order is not None:
            raise ValidationError(
                {
                    "is_follow_up": (
                        "is_follow_up must be True when "
                        "previous_order_id is provided."
                    )
                }
            )

    @staticmethod
    def _validate_unpaid_access(
        *,
        attrs: dict[str, Any],
        request_user: Any,
    ) -> None:
        """
        Validate unpaid access permission.

        Args:
            attrs:
                Incoming normalized request data.
            request_user:
                Current authenticated user.

        Raises:
            ValidationError:
                Raised when unpaid access is not allowed.
        """
        allow_unpaid_access = attrs.get("allow_unpaid_access", False)
        if allow_unpaid_access and not getattr(
            request_user,
            "is_staff",
            False,
        ):
            raise ValidationError(
                {
                    "allow_unpaid_access": (
                        "Only staff can enable allow_unpaid_access."
                    )
                }
            )

    @staticmethod
    def _validate_preferred_writer_tenant(
        *,
        context: OrderCreationContext,
        request_user: Any,
    ) -> None:
        """
        Validate preferred writer tenant consistency.

        Args:
            context:
                Resolved creation context.
            request_user:
                Current authenticated user.

        Raises:
            ValidationError:
                Raised when tenant linkage is invalid.
        """
        preferred_writer = context.preferred_writer
        if preferred_writer is None:
            return

        writer_website_id = getattr(
            preferred_writer,
            "website_id",
            None,
        )
        request_website_id = getattr(request_user, "website_id", None)

        if (
            writer_website_id is not None
            and request_website_id is not None
            and writer_website_id != request_website_id
        ):
            raise ValidationError(
                {
                    "preferred_writer_id": (
                        "Preferred writer must belong to the same tenant."
                    )
                }
            )

    @staticmethod
    def _validate_previous_order_tenant(
        *,
        context: OrderCreationContext,
        request_user: Any,
    ) -> None:
        """
        Validate previous order tenant consistency.

        Args:
            context:
                Resolved creation context.
            request_user:
                Current authenticated user.

        Raises:
            ValidationError:
                Raised when tenant linkage is invalid.
        """
        previous_order = context.previous_order
        if previous_order is None:
            return

        previous_order_website = getattr(previous_order, "website", None)
        previous_order_website_id = getattr(
            previous_order_website,
            "pk",
            None,
        )
        request_website_id = getattr(request_user, "website_id", None)

        if (
            previous_order_website_id is not None
            and request_website_id is not None
            and previous_order_website_id != request_website_id
        ):
            raise ValidationError(
                {
                    "previous_order_id": (
                        "Previous order must belong to the same tenant."
                    )
                }
            )

    @staticmethod
    def _validate_pricing_snapshot_matches_request(
        *,
        attrs: dict[str, Any],
        context: OrderCreationContext,
    ) -> None:
        """
        Validate pricing snapshot alignment with request intent.

        Args:
            attrs:
                Incoming normalized request data.
            context:
                Resolved creation context.

        Raises:
            ValidationError:
                Raised when pricing snapshot and request mismatch.
        """
        pricing_snapshot = context.pricing_snapshot

        requested_service_family = attrs.get("service_family")
        requested_service_code = attrs.get("service_code")

        snapshot_service_family = getattr(
            pricing_snapshot,
            "service_family",
            "",
        )
        snapshot_service_code = getattr(
            pricing_snapshot,
            "service_code",
            "",
        )

        if (
            requested_service_family
            and requested_service_family != snapshot_service_family
        ):
            raise ValidationError(
                {
                    "pricing_snapshot_id": (
                        "Selected pricing snapshot does not match "
                        "requested service_family."
                    )
                }
            )

        if (
            requested_service_code
            and requested_service_code != snapshot_service_code
        ):
            raise ValidationError(
                {
                    "pricing_snapshot_id": (
                        "Selected pricing snapshot does not match "
                        "requested service_code."
                    )
                }
            )

        snapshot_website_id = getattr(
            pricing_snapshot,
            "website_id",
            None,
        )
        request_website_id = getattr(
            attrs.get("request_user"),
            "website_id",
            None,
        )

        if (
            snapshot_website_id is not None
            and request_website_id is not None
            and snapshot_website_id != request_website_id
        ):
            raise ValidationError(
                {
                    "pricing_snapshot_id": (
                        "Selected pricing snapshot must belong to the "
                        "same tenant."
                    )
                }
            )