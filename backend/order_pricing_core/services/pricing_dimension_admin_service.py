"""
Admin service for pricing dimension management.
"""

from __future__ import annotations

from django.db import transaction

from order_pricing_core.models import AcademicLevelRate
from order_pricing_core.models import AnalysisLevelRate
from order_pricing_core.models import DeadlineRate
from order_pricing_core.models import DiagramComplexityRate
from order_pricing_core.models import PaperTypeRate
from order_pricing_core.models import SubjectRate
from order_pricing_core.models import WorkTypeRate
from order_pricing_core.models import WriterLevelRate
from order_pricing_core.validators.pricing_dimension_validators import (
    validate_deadline_rate,
)
from order_pricing_core.validators.pricing_dimension_validators import (
    validate_non_negative_amount,
)
from order_pricing_core.validators.pricing_dimension_validators import (
    validate_positive_multiplier,
)
from order_pricing_core.validators.pricing_dimension_validators import (
    validate_subject_rate,
)


class PricingDimensionAdminService:
    """
    Admin-facing service for pricing dimension management.
    """

    @classmethod
    @transaction.atomic
    def create_academic_level_rate(
        cls,
        *,
        website,
        data: dict,
    ) -> AcademicLevelRate:
        """
        Create an academic level rate.
        """
        validate_positive_multiplier(
            multiplier=data["multiplier"],
        )
        return AcademicLevelRate.objects.create(
            website=website,
            **data,
        )

    @classmethod
    @transaction.atomic
    def create_paper_type_rate(
        cls,
        *,
        website,
        data: dict,
    ) -> PaperTypeRate:
        """
        Create a paper type rate.
        """
        validate_positive_multiplier(
            multiplier=data["multiplier"],
        )
        return PaperTypeRate.objects.create(
            website=website,
            **data,
        )

    @classmethod
    @transaction.atomic
    def create_work_type_rate(
        cls,
        *,
        website,
        data: dict,
    ) -> WorkTypeRate:
        """
        Create a work type rate.
        """
        validate_positive_multiplier(
            multiplier=data["multiplier"],
        )
        return WorkTypeRate.objects.create(
            website=website,
            **data,
        )

    @classmethod
    @transaction.atomic
    def create_deadline_rate(
        cls,
        *,
        website,
        data: dict,
    ) -> DeadlineRate:
        """
        Create a deadline rate.
        """
        validate_deadline_rate(
            max_hours=data["max_hours"],
            multiplier=data["multiplier"],
        )
        return DeadlineRate.objects.create(
            website=website,
            **data,
        )

    @classmethod
    @transaction.atomic
    def create_writer_level_rate(
        cls,
        *,
        website,
        data: dict,
    ) -> WriterLevelRate:
        """
        Create a writer level rate.
        """
        if data.get("is_flat_fee", True):
            validate_non_negative_amount(
                amount=data["amount"],
            )
        else:
            validate_positive_multiplier(
                multiplier=data["amount"],
                field_name="amount",
            )

        return WriterLevelRate.objects.create(
            website=website,
            **data,
        )

    @classmethod
    @transaction.atomic
    def create_analysis_level_rate(
        cls,
        *,
        website,
        data: dict,
    ) -> AnalysisLevelRate:
        """
        Create an analysis level rate.
        """
        validate_positive_multiplier(
            multiplier=data["multiplier"],
        )
        return AnalysisLevelRate.objects.create(
            website=website,
            **data,
        )

    @classmethod
    @transaction.atomic
    def create_diagram_complexity_rate(
        cls,
        *,
        website,
        data: dict,
    ) -> DiagramComplexityRate:
        """
        Create a diagram complexity rate.
        """
        validate_positive_multiplier(
            multiplier=data["multiplier"],
        )
        return DiagramComplexityRate.objects.create(
            website=website,
            **data,
        )

    @classmethod
    @transaction.atomic
    def create_subject_rate(
        cls,
        *,
        website,
        data: dict,
    ) -> SubjectRate:
        """
        Create a subject rate.
        """
        subject_rate = SubjectRate(
            website=website,
            **data,
        )
        validate_subject_rate(subject_rate)
        subject_rate.save()
        return subject_rate