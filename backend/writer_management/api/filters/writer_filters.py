"""
writer_management/api/filters/writer_filters.py

Django-filter FilterSets for writer_management API endpoints.

Used by views to provide querystring filtering.
e.g. GET /api/writers/?onboarding_status=completed&is_verified=true
"""

import django_filters

from writer_management.models.writer_profile import WriterProfile
from writer_management.models.writer_application import WriterApplication
from writer_management.models.writer_discipline import (
    WriterSuspension,
    WriterBlacklist,
)
from writer_management.models.writer_warning import WriterWarning
from writer_management.models.writer_strike import WriterStrike
from writer_management.models.writer_performance import WriterPerformanceSnapshot
from writer_management.enums import (
    WriterOnboardingStatus,
    WriterVerificationStatus,
)


class WriterProfileFilter(django_filters.FilterSet):
    """
    Filter writers by profile fields.
    Used by admin list views.
    """

    onboarding_status = django_filters.ChoiceFilter(
        choices=WriterOnboardingStatus.choices,
    )
    verification_status = django_filters.ChoiceFilter(
        choices=WriterVerificationStatus.choices,
    )
    is_verified = django_filters.BooleanFilter()
    is_deleted = django_filters.BooleanFilter()
    level = django_filters.NumberFilter(field_name="writer_level__id")
    level_name = django_filters.CharFilter(
        field_name="writer_level__name",
        lookup_expr="iexact",
    )
    joined_after = django_filters.DateTimeFilter(
        field_name="joined_at",
        lookup_expr="gte",
    )
    joined_before = django_filters.DateTimeFilter(
        field_name="joined_at",
        lookup_expr="lte",
    )
    search = django_filters.CharFilter(
        method="filter_search",
        label="Search registration_id or pen_name",
    )

    class Meta:
        model = WriterProfile
        fields = [
            "onboarding_status",
            "verification_status",
            "is_verified",
            "is_deleted",
        ]

    def filter_search(self, queryset, name, value):
        from django.db.models import Q
        return queryset.filter(
            Q(registration_id__icontains=value) |
            Q(pen_name__icontains=value)
        )


class WriterApplicationFilter(django_filters.FilterSet):
    """Filter writer applications by status and submission date."""

    status = django_filters.ChoiceFilter(
        choices=WriterApplication.Status.choices,
    )
    submitted_after = django_filters.DateTimeFilter(
        field_name="submitted_at",
        lookup_expr="gte",
    )
    submitted_before = django_filters.DateTimeFilter(
        field_name="submitted_at",
        lookup_expr="lte",
    )
    search = django_filters.CharFilter(
        method="filter_search",
        label="Search name or email",
    )

    class Meta:
        model = WriterApplication
        fields = ["status"]

    def filter_search(self, queryset, name, value):
        from django.db.models import Q
        return queryset.filter(
            Q(full_name__icontains=value) |
            Q(email__icontains=value)
        )


class WriterWarningFilter(django_filters.FilterSet):
    """Filter writer warnings."""

    category = django_filters.CharFilter()
    is_active = django_filters.BooleanFilter()
    is_voided = django_filters.BooleanFilter()
    issued_after = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
    )
    issued_before = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="lte",
    )

    class Meta:
        model = WriterWarning
        fields = ["category", "is_active", "is_voided"]


class WriterStrikeFilter(django_filters.FilterSet):
    """Filter writer strikes."""

    category = django_filters.CharFilter()
    is_voided = django_filters.BooleanFilter()
    issued_after = django_filters.DateTimeFilter(
        field_name="issued_at",
        lookup_expr="gte",
    )

    class Meta:
        model = WriterStrike
        fields = ["category", "is_voided"]


class WriterPerformanceSnapshotFilter(django_filters.FilterSet):
    """Filter performance snapshots by period."""

    period_start = django_filters.DateFilter()
    period_end = django_filters.DateFilter()
    is_processed = django_filters.BooleanFilter()
    period_start_after = django_filters.DateFilter(
        field_name="period_start",
        lookup_expr="gte",
    )
    period_end_before = django_filters.DateFilter(
        field_name="period_end",
        lookup_expr="lte",
    )

    class Meta:
        model = WriterPerformanceSnapshot
        fields = ["is_processed"]