import django_filters


class BaseFilterSet(django_filters.FilterSet):
    """
    Base filter set for all financial modules.

    Keeps filtering consistent across:
    - settlements
    - financial events
    - exposures
    - payouts
    """

    ordering = django_filters.OrderingFilter(
        fields=(
            ("created_at", "created_at"),
            ("updated_at", "updated_at"),
        )
    )
