import django_filters
from tips.models.tip import Tip


class TipFilter(django_filters.FilterSet):
    """
    Filtering for tips list endpoint.
    """

    sender_id = django_filters.NumberFilter(field_name="sender_id")
    receiver_id = django_filters.NumberFilter(field_name="receiver_id")
    status = django_filters.CharFilter(field_name="status")

    class Meta:
        model = Tip
        fields = ["sender_id", "receiver_id", "status"]