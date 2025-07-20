import django_filters
from notifications_system.models.notifications import Notification

class NotificationFilter(django_filters.FilterSet):
    """
    Filter for notifications based on user and type.
    """
    is_read = django_filters.BooleanFilter(field_name='is_read', lookup_expr='exact')
    category = django_filters.CharFilter(field_name='category', lookup_expr='icontains')
    is_critical = django_filters.BooleanFilter(field_name='is_critical', lookup_expr='exact')
    is_digest = django_filters.BooleanFilter(field_name='is_digest', lookup_expr='exact')
    event = django_filters.CharFilter(field_name='event', lookup_expr='icontains')
    category = django_filters.CharFilter(field_name='category', lookup_expr='iexact')
    priority = django_filters.NumberFilter(field_name='priority', lookup_expr='exact')
    digest_group = django_filters.CharFilter(field_name='digest_group', lookup_expr='iexact')
    sent_at = django_filters.DateTimeFromToRangeFilter(field_name='sent_at')
    created_at = django_filters.DateTimeFromToRangeFilter(field_name='created_at')
    user_id = django_filters.NumberFilter(field_name='user__id', lookup_expr='exact')
    user_email = django_filters.CharFilter(field_name='user__email', lookup_expr='icontains')
    user_username = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    user = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    type = django_filters.CharFilter(field_name='type', lookup_expr='exact')

    class Meta:
        model = Notification
        fields = ['user', 'type']
        filter_overrides = {
            django_filters.CharFilter: {
                'filter_class': django_filters.CharFilter
            },
            django_filters.NumberFilter: {
                'filter_class': django_filters.NumberFilter
            },
            django_filters.BooleanFilter: {
                'filter_class': django_filters.BooleanFilter
            },
            django_filters.DateTimeFromToRangeFilter: {
                'filter_class': django_filters.DateTimeFromToRangeFilter
            },
        }
        # Additional configuration can go here  
        # such as ordering, pagination, etc.
        ordering = ['-sent_at']
        ordering_fields = ['sent_at', 'created_at', 'priority']
        pagination = {
            'page_size': 10,
            'max_page_size': 100
        }