from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import timedelta
from decimal import Decimal
from typing import Any, Optional, cast

from django.core.exceptions import ValidationError
from django.db import transaction

from orders.models.orders.enums import OrderPaymentStatus, OrderStatus
from orders.models.orders.order import Order
from orders.models.orders.order_item import OrderItem
from orders.models.orders.order_timeline_event import OrderTimelineEvent
from orders.services.order_pricing_snapshot_service import (
    OrderPricingSnapshotService,
)
from django.forms.models import model_to_dict

class OrderCreationService:
    """
    Own creation of new orders from validated input and pricing-core output.

    Responsibilities:
        1. Create the order aggregate.
        2. Create order items.
        3. Store current upstream pricing snapshot on the order.
        4. Record frozen order-side pricing history.
        5. Initialize payment fields and workflow state.

    Important:
        This service consumes pricing-core output.
        It does not calculate prices itself.
    """

    TIMELINE_EVENT_CREATED = "created"

    @classmethod
    @transaction.atomic
    def create_order(
        cls,
        *,
        website: Any,
        client: Any,
        order_payload: dict[str, Any],
        pricing_result: Any,
        source_pricing_snapshot: Optional[Any] = None,
        triggered_by: Optional[Any] = None,
    ) -> Order:
        """
        Create a new order from validated payload and pricing-core result.
        
        Args:
            website: The website/tenant for the order.
            client: The client placing the order.
            order_payload: Validated input data for the order creation, containing
                fields like topic, paper_type, client_deadline, etc.
            pricing_result: The raw output from pricing-core, containing calculated
                prices and related metadata. This is used as the source of truth for
                pricing details on the order and items.
            source_pricing_snapshot: Optional original pricing snapshot object from
                pricing-core, included for reference but not directly used in the
                payload construction.
            triggered_by: Optional user or system actor responsible for triggering
                the order creation, recorded on timeline events.


        Returns:
            Order: The created order instance with related items and pricing history.

        Raises:
            ValidationError: If required fields are missing from the payload.
        """
        cls._validate_payload(order_payload=order_payload)
        snapshot_payload = cls._build_snapshot_payload(
            pricing_result=pricing_result,
            source_pricing_snapshot=source_pricing_snapshot,
        )

        total_price = cls._to_decimal(
            cls._extract_value(
                pricing_result=pricing_result,
                key="total_price",
                default="0.00",
            )
        )
        subtotal_amount = cls._to_decimal(
            cls._extract_value(
                pricing_result=pricing_result,
                key="subtotal_amount",
                default=total_price,
            )
        )
        discount_amount = cls._to_decimal(
            cls._extract_value(
                pricing_result=pricing_result,
                key="discount_amount",
                default="0.00",
            )
        )
        writer_compensation_amount = cls._to_decimal(
            cls._extract_value(
                pricing_result=pricing_result,
                key="writer_compensation_amount",
                default="0.00",
            )
        )

        client_deadline = order_payload["client_deadline"]
        writer_deadline = cls._resolve_writer_deadline(
            client_deadline=client_deadline,
            order_payload=order_payload,
        )

        initial_payment_status = (
            OrderPaymentStatus.FULLY_PAID
            if total_price == Decimal("0.00")
            else OrderPaymentStatus.UNPAID
        )
        initial_status = (
            OrderStatus.READY_FOR_STAFFING
            if total_price == Decimal("0.00")
            else OrderStatus.PENDING_PAYMENT
        )

        order = Order.objects.create(
            website=website,
            client=client,
            topic=order_payload["topic"],
            paper_type=order_payload["paper_type"],
            academic_level=order_payload.get("academic_level"),
            formatting_style=order_payload.get("formatting_style"),
            subject=order_payload.get("subject"),
            type_of_work=order_payload.get("type_of_work"),
            english_type=order_payload.get("english_type"),
            writer_level=order_payload.get("writer_level"),
            discount=order_payload.get("discount"),
            discount_code_used=order_payload.get(
                "discount_code_used",
                "",
            ),
            is_follow_up=order_payload.get("is_follow_up", False),
            previous_order=order_payload.get("previous_order"),
            status=initial_status,
            visibility_mode=order_payload.get(
                "visibility_mode",
                ""
            ) or "hidden",
            preferred_writer=order_payload.get("preferred_writer"),
            preferred_writer_fee_amount=cls._to_decimal(
                cls._extract_value(
                    pricing_result=pricing_result,
                    key="preferred_writer_fee_amount",
                    default="0.00",
                )
            ),
            flags=order_payload.get("flags", []),
            client_deadline=client_deadline,
            writer_deadline=writer_deadline,
            total_price=total_price,
            amount_paid=Decimal("0.00"),
            currency=cls._extract_value(
                pricing_result=pricing_result,
                key="currency",
                default="USD",
            ),
            payment_status=initial_payment_status,
            writer_compensation=writer_compensation_amount,
            pricing_snapshot=source_pricing_snapshot,
            service_family=cls._extract_value(
                pricing_result=pricing_result,
                key="service_family",
                default=order_payload.get("service_family", ""),
            ),
            service_code=cls._extract_value(
                pricing_result=pricing_result,
                key="service_code",
                default=order_payload.get("service_code", ""),
            ),
            is_composite=bool(
                cls._extract_value(
                    pricing_result=pricing_result,
                    key="is_composite",
                    default=False,
                )
            ),
            is_urgent=order_payload.get("is_urgent", False),
            requires_editing=order_payload.get("requires_editing"),
            editing_skip_reason=order_payload.get(
                "editing_skip_reason",
                "",
            ),
            created_by_admin=order_payload.get(
                "created_by_admin",
                False,
            ),
            order_instructions=order_payload["order_instructions"],
            external_contact_name=order_payload.get(
                "external_contact_name",
                "",
            ),
            external_contact_email=order_payload.get(
                "external_contact_email",
                "",
            ),
            external_contact_phone=order_payload.get(
                "external_contact_phone",
                "",
            ),
            allow_unpaid_access=order_payload.get(
                "allow_unpaid_access",
                False,
            ),
        )

        cls._create_order_items(
            order=order,
            website=website,
            pricing_result=pricing_result,
            source_pricing_snapshot=source_pricing_snapshot,
        )

        OrderPricingSnapshotService.record_current_snapshot(
            order=order,
            source_pricing_snapshot=source_pricing_snapshot,
            subtotal_amount=subtotal_amount,
            discount_amount=discount_amount,
            total_amount=total_price,
            writer_compensation_amount=writer_compensation_amount,
            pricing_payload=snapshot_payload,
            created_by=triggered_by or client,
            currency=order.currency,
            pricing_policy_version=str(
                cls._extract_value(
                    pricing_result=pricing_result,
                    key="pricing_policy_version",
                    default="",
                )
            ),
        )

        cls._create_timeline_event(
            order=order,
            actor=triggered_by or client,
            metadata={
                "total_price": str(order.total_price),
                "service_family": order.service_family,
                "service_code": order.service_code,
                "payment_status": order.payment_status,
            },
        )
        return order

    @staticmethod
    def _validate_payload(*, order_payload: dict[str, Any]) -> None:
        required_fields = {
            "topic",
            "paper_type",
            "client_deadline",
            "order_instructions",
        }
        missing = [
            field for field in required_fields
            if field not in order_payload
        ]
        if missing:
            raise ValidationError(
                {"missing_fields": f"Missing required fields: {missing}"}
            )

    @classmethod
    def _create_order_items(
        cls,
        *,
        order: Order,
        website: Any,
        pricing_result: Any,
        source_pricing_snapshot: Optional[Any],
    ) -> None:
        """
        Create frozen order items from the pricing result.
        Each item is created based on the extracted
        details from the pricing result,
        and is associated with the order and the
        source pricing snapshot for reference.

        Args:
            order:
                The order instance to which the items will be linked.
            website:
                The website/tenant for the order.
            pricing_result:
                The raw output from pricing-core, which contains
                the details of the items to be created.
                This is the source of truth for item details.
            source_pricing_snapshot:
                The original pricing snapshot object from pricing-core,
                if available. This is included for reference but
                the item details are derived from the raw pricing
                result to ensure decoupling from pricing-core's internal models.
        Returns:
            None:
                This method creates order items as a side effect
                and does not return anything.
        """
        items = cls._extract_items(pricing_result=pricing_result)
        for index, item in enumerate(items):
            OrderItem.objects.create(
                website=website,
                order=order,
                pricing_snapshot=source_pricing_snapshot,
                service_family=item.get(
                    "service_family",
                    order.service_family,
                ),
                service_code=item.get(
                    "service_code",
                    order.service_code,
                ),
                topic=item.get("topic", ""),
                quantity=int(item.get("quantity", 1)),
                subtotal=cls._to_decimal(
                    item.get("subtotal", "0.00")
                ),
                discount_amount=cls._to_decimal(
                    item.get("discount_amount", "0.00")
                ),
                total_price=cls._to_decimal(
                    item.get("total_price", "0.00")
                ),
                metadata=item.get("metadata", {}),
                sort_order=index,
            )

    @staticmethod
    def _resolve_writer_deadline(
        *,
        client_deadline,
        order_payload: dict[str, Any],
    ):
        """
        Resolve internal writer deadline based on client deadline
        and any explicit override in the payload.

        Args:
            client_deadline:
                The deadline by which the client expects
                the order to be completed.
            order_payload:
                The validated input payload for order creation,
                which may contain an explicit writer deadline.

        Returns:
            datetime:
                The resolved writer deadline,
                which is either the explicit writer deadline
                from the payload or a default offset from the client deadline.
        """
        explicit_writer_deadline = order_payload.get("writer_deadline")
        if explicit_writer_deadline is not None:
            return explicit_writer_deadline
        return client_deadline - timedelta(minutes=30)

    @staticmethod
    def _extract_items(
        *,
        pricing_result: Any
    ) -> list[dict[str, Any]]:
        """
        Extract a list of items from the pricing result, handling
        different possible types.

        Asumes that the items are located under the "items"
        key if the result is a dict,
        or as an "items" attribute if it's an object.
        The items themselves are expected.

        Args:
            pricing_result: 
                The raw output from pricing-core,
                which may be in various formats. 

        Returns:
            list[dict[str, Any]]:
                Item list.
            (A list of dictionaries representing the items,
            or an empty list if not found.)
        """
        if isinstance(pricing_result, dict):
            return cast(
                list[dict[str, Any]],
                pricing_result.get("items", []),
            )
        return cast(
            list[dict[str, Any]],
            getattr(pricing_result, "items", []),
        )

    @staticmethod
    def _extract_value(
        *,
        pricing_result: Any,
        key: str,
        default: Any,
    ) -> Any:
        """
        Extract a value from the pricing result, handling
        different possible types.
        The pricing_result may be a dict, a dataclass,
        or an arbitrary object with attributes.

            Args:
                pricing_result:
                    The raw output from pricing-core,
                    which may be in various formats.
                key: 
                    The key or attribute name to extract
                    from the pricing result.
                default: 
                    The default value to return if the
                    key/attribute is not found.

            Returns:
                The extracted value if found, otherwise the default.

        """
        if isinstance(pricing_result, dict):
            return pricing_result.get(key, default)
        return getattr(pricing_result, key, default)

    @staticmethod
    def _build_snapshot_payload(
        *,
        pricing_result: Any,
        source_pricing_snapshot: Optional[Any] = None,
    ) -> dict[str, Any]:
        """
        Build a JSON-serializable pricing payload for
        the order-side history record.

        Args:
            pricing_result:
                The raw output from pricing-core, which may be a dict, dataclass,
                or an arbitrary object with attributes. This is the source of truth
                for the pricing state to be recorded on the order.
            source_pricing_snapshot:
                The original pricing snapshot object from pricing-core, if available.
                This is included for reference but the rest of the payload is derived
                from the raw result to ensure it is decoupled from pricing-core's
                internal models and is JSON-serializable.
                Optional upstream pricing snapshot model instance,
                included for reference but not directly used.

        Returns:
            dict[str, Any]:
                A JSON-serializable dictionary representing the pricing state,
                derived from the raw pricing result.
        """
        if isinstance(pricing_result, dict):
            return pricing_result
        if is_dataclass(pricing_result) and not isinstance(
            pricing_result, type
        ):
            return cast(dict[str, Any], asdict(pricing_result))
        
        if source_pricing_snapshot is not None:
            payload = model_to_dict(source_pricing_snapshot)
            
            for key, value in list(payload.items()):
                if isinstance(value, Decimal):
                    payload[key] = str(value)


            payload["source_pricing_snapshot_id"] = getattr(
                source_pricing_snapshot,
                "pk",
                None,
            )

            return cast(dict[str, Any], payload)

        payload: dict[str, Any] = {}
        for attr in dir(pricing_result):
            if attr.startswith("_"):
                continue

            value = getattr(pricing_result, attr)
            if isinstance(value, Decimal):
                payload[attr] = str(value)
            else:
                payload[attr] = value

        return payload

    @staticmethod
    def _create_timeline_event(
        *,
        order: Order,
        actor: Optional[Any],
        metadata: dict[str, Any],
    ) -> OrderTimelineEvent:
        """
        Create an initial order-created timeline event.

        Args:
            order:
                The order for which to create the timeline event.
            actor: 
                The user or system actor responsible for the order creation,
                if available.
            metadata:
                Additional data to include in the timeline event.

        Returns:
            OrderTimelineEvent:
                The created timeline event instance.
        """
        return OrderTimelineEvent.objects.create(
            website=order.website,
            order=order,
            event_type=OrderCreationService.TIMELINE_EVENT_CREATED,
            actor=actor,
            metadata=metadata,
        )

    @staticmethod
    def _to_decimal(value: Any) -> Decimal:
        """
        Convert a value to Decimal, ensuring that strings and other types are handled.
         Args:
             value: The value to convert, which may be a Decimal, string, or other type.
             
            Returns:
                Decimal: The converted Decimal value.
        """
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))