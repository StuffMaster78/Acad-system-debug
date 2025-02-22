from django.urls import path
from .views import NotificationViewSet, NotificationPreferenceViewSet

urlpatterns = [
    path('notifications/', NotificationViewSet.as_view({'get': 'list', 'post': 'create'}), name='notifications-list'),
    path('notifications/<int:pk>/', NotificationViewSet.as_view({'get': 'retrieve'}), name='notification-detail'),
    path('notifications/<int:pk>/mark-as-read/', NotificationViewSet.as_view({'post': 'mark_as_read'}), name='mark-as-read'),
    path('notifications/mark-all-as-read/', NotificationViewSet.as_view({'post': 'mark_all_as_read'}), name='mark-all-as-read'),
    path('preferences/', NotificationPreferenceViewSet.as_view({'get': 'list', 'post': 'create', 'patch': 'update'}), name='notification-preferences'),
]