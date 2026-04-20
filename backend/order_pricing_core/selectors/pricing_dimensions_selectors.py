"""
Pricing dimension selectors for the order_pricing_core app.
"""

from __future__ import annotations

from django.core.exceptions import ValidationError

from order_pricing_core.models import AcademicLevelRate
from order_pricing_core.models import AnalysisLevelRate
from order_pricing_core.models import DeadlineRate
from order_pricing_core.models import DiagramComplexityRate
from order_pricing_core.models import PaperTypeRate
from order_pricing_core.models import SubjectCategory
from order_pricing_core.models import SubjectRate
from order_pricing_core.models import WorkTypeRate
from order_pricing_core.models import WriterLevelRate


def get_academic_level_rate_by_id(
    *,
    website,
    item_id: int,
) -> AcademicLevelRate:
    try:
        return AcademicLevelRate.objects.get(
            id=item_id,
            website=website,
        )
    except AcademicLevelRate.DoesNotExist as exc:
        raise ValidationError(
            {"item_id": "Academic level rate not found."}
        ) from exc


def get_paper_type_rate_by_id(
    *,
    website,
    item_id: int,
) -> PaperTypeRate:
    try:
        return PaperTypeRate.objects.get(
            id=item_id,
            website=website,
        )
    except PaperTypeRate.DoesNotExist as exc:
        raise ValidationError(
            {"item_id": "Paper type rate not found."}
        ) from exc


def get_work_type_rate_by_id(
    *,
    website,
    item_id: int,
) -> WorkTypeRate:
    try:
        return WorkTypeRate.objects.get(
            id=item_id,
            website=website,
        )
    except WorkTypeRate.DoesNotExist as exc:
        raise ValidationError(
            {"item_id": "Work type rate not found."}
        ) from exc


def get_deadline_rate_by_id(
    *,
    website,
    item_id: int,
) -> DeadlineRate:
    try:
        return DeadlineRate.objects.get(
            id=item_id,
            website=website,
        )
    except DeadlineRate.DoesNotExist as exc:
        raise ValidationError(
            {"item_id": "Deadline rate not found."}
        ) from exc


def get_subject_category_by_id(
    *,
    website,
    item_id: int,
) -> SubjectCategory:
    try:
        return SubjectCategory.objects.get(
            id=item_id,
            website=website,
        )
    except SubjectCategory.DoesNotExist as exc:
        raise ValidationError(
            {"item_id": "Subject category not found."}
        ) from exc


def get_subject_rate_by_id(
    *,
    website,
    item_id: int,
) -> SubjectRate:
    try:
        return SubjectRate.objects.select_related("category").get(
            id=item_id,
            website=website,
        )
    except SubjectRate.DoesNotExist as exc:
        raise ValidationError(
            {"item_id": "Subject rate not found."}
        ) from exc


def get_writer_level_rate_by_id(
    *,
    website,
    item_id: int,
) -> WriterLevelRate:
    try:
        return WriterLevelRate.objects.get(
            id=item_id,
            website=website,
        )
    except WriterLevelRate.DoesNotExist as exc:
        raise ValidationError(
            {"item_id": "Writer level rate not found."}
        ) from exc


def get_analysis_level_rate_by_id(
    *,
    website,
    item_id: int,
) -> AnalysisLevelRate:
    try:
        return AnalysisLevelRate.objects.get(
            id=item_id,
            website=website,
        )
    except AnalysisLevelRate.DoesNotExist as exc:
        raise ValidationError(
            {"item_id": "Analysis level rate not found."}
        ) from exc


def get_diagram_complexity_rate_by_id(
    *,
    website,
    item_id: int,
) -> DiagramComplexityRate:
    try:
        return DiagramComplexityRate.objects.get(
            id=item_id,
            website=website,
        )
    except DiagramComplexityRate.DoesNotExist as exc:
        raise ValidationError(
            {"item_id": "Diagram complexity rate not found."}
        ) from exc