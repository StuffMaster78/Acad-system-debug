from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any

from django.contrib.auth import get_user_model

from discounts.models import Discount
from order_configs.models import (
    AcademicLevel,
    FormattingandCitationStyle,
    EnglishType,
    PaperType,
    Subject,
    TypeOfWork,
)
from order_pricing_core.models.pricing_snapshots import PricingSnapshot
from order_pricing_core.models.pricing_dimensions import WriterLevelRate
from orders.models import Order


UserModel = get_user_model()


@dataclass(frozen=True)
class OrderCreationContext:
    """
    Hold resolved model instances needed for order creation.

    This bundles related objects so services and views do not need to
    perform repeated lookup logic.
    """

    paper_type: PaperType
    pricing_snapshot: PricingSnapshot
    academic_level: Optional[AcademicLevel] = None
    formatting_style: Optional[FormattingandCitationStyle] = None
    subject: Optional[Subject] = None
    type_of_work: Optional[TypeOfWork] = None
    english_type: Optional[EnglishType] = None
    writer_level: Optional[WriterLevelRate] = None
    discount: Optional[Discount] = None
    previous_order: Optional[Order] = None
    preferred_writer: Optional[Any] = None


class OrderCreationSelector:
    """
    Resolve related objects required by order creation workflow.

    Responsibilities:
        1. Resolve config objects from incoming ids.
        2. Resolve pricing snapshot selected in pricing core.
        3. Resolve optional previous order and preferred writer.
        4. Bundle these into a single context object.

    This is read-only logic. It must not mutate database state.
    """

    @classmethod
    def build_context(
        cls,
        *,
        paper_type_id: int,
        pricing_snapshot_id: int,
        academic_level_id: Optional[int] = None,
        formatting_style_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        type_of_work_id: Optional[int] = None,
        english_type_id: Optional[int] = None,
        writer_level_id: Optional[int] = None,
        discount_id: Optional[int] = None,
        previous_order_id: Optional[int] = None,
        preferred_writer_id: Optional[int] = None,
    ) -> OrderCreationContext:
        """
        Resolve and bundle order creation dependencies.

        Args:
            paper_type_id:
                Paper type primary key.
            pricing_snapshot_id:
                Pricing snapshot primary key.
            academic_level_id:
                Optional academic level primary key.
            formatting_style_id:
                Optional formatting style primary key.
            subject_id:
                Optional subject primary key.
            type_of_work_id:
                Optional type of work primary key.
            english_type_id:
                Optional English type primary key.
            writer_level_id:
                Optional writer level primary key.
            discount_id:
                Optional discount primary key.
            previous_order_id:
                Optional previous order primary key.
            preferred_writer_id:
                Optional preferred writer primary key.

        Returns:
            OrderCreationContext:
                Bundled resolved instances.
        """
        return OrderCreationContext(
            paper_type=PaperType.objects.get(pk=paper_type_id),
            pricing_snapshot=PricingSnapshot.objects.get(
                pk=pricing_snapshot_id
            ),
            academic_level=cls._get_optional_academic_level(
                academic_level_id
            ),
            formatting_style=cls._get_optional_formatting_style(
                formatting_style_id
            ),
            subject=cls._get_optional_subject(subject_id),
            type_of_work=cls._get_optional_type_of_work(
                type_of_work_id
            ),
            english_type=cls._get_optional_english_type(
                english_type_id
            ),
            writer_level=cls._get_optional_writer_level(
                writer_level_id
            ),
            discount=cls._get_optional_discount(discount_id),
            previous_order=cls._get_optional_previous_order(
                previous_order_id
            ),
            preferred_writer=cls._get_optional_preferred_writer(
                preferred_writer_id
            ),
        )

    @staticmethod
    def _get_optional_academic_level(
        academic_level_id: Optional[int],
    ) -> Optional[AcademicLevel]:
        """
        Resolve academic level when provided.
        """
        if academic_level_id is None:
            return None
        return AcademicLevel.objects.get(pk=academic_level_id)

    @staticmethod
    def _get_optional_formatting_style(
        formatting_style_id: Optional[int],
    ) -> Optional[FormattingandCitationStyle]:
        """
        Resolve formatting style when provided.
        """
        if formatting_style_id is None:
            return None
        return FormattingandCitationStyle.objects.get(
            pk=formatting_style_id
        )

    @staticmethod
    def _get_optional_subject(
        subject_id: Optional[int],
    ) -> Optional[Subject]:
        """
        Resolve subject when provided.
        """
        if subject_id is None:
            return None
        return Subject.objects.get(pk=subject_id)

    @staticmethod
    def _get_optional_type_of_work(
        type_of_work_id: Optional[int],
    ) -> Optional[TypeOfWork]:
        """
        Resolve type of work when provided.
        """
        if type_of_work_id is None:
            return None
        return TypeOfWork.objects.get(pk=type_of_work_id)

    @staticmethod
    def _get_optional_english_type(
        english_type_id: Optional[int],
    ) -> Optional[EnglishType]:
        """
        Resolve English type when provided.
        """
        if english_type_id is None:
            return None
        return EnglishType.objects.get(pk=english_type_id)

    @staticmethod
    def _get_optional_writer_level(
        writer_level_id: Optional[int],
    ) -> Optional[WriterLevelRate]:
        """
        Resolve writer level when provided.
        """
        if writer_level_id is None:
            return None
        return WriterLevelRate.objects.get(pk=writer_level_id)

    @staticmethod
    def _get_optional_discount(
        discount_id: Optional[int],
    ) -> Optional[Discount]:
        """
        Resolve discount when provided.
        """
        if discount_id is None:
            return None
        return Discount.objects.get(pk=discount_id)

    @staticmethod
    def _get_optional_previous_order(
        previous_order_id: Optional[int],
    ) -> Optional[Order]:
        """
        Resolve previous order when provided.
        """
        if previous_order_id is None:
            return None
        return Order.all_objects.get(pk=previous_order_id)

    @staticmethod
    def _get_optional_preferred_writer(
        preferred_writer_id: Optional[int],
    ) -> Optional[Any]:
        """
        Resolve preferred writer when provided.
        """
        if preferred_writer_id is None:
            return None
        return UserModel.objects.get(pk=preferred_writer_id)