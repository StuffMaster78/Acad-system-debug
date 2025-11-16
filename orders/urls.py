from django.urls import path, include
from rest_framework.routers import DefaultRouter

from orders.views.writers.reassignment_log_viewset import WriterReassignmentLogViewSet
from .views.orders.base import OrderBaseViewSet
from .views.orders.disputes import DisputeViewSet
from .views.writers.writer_requests import WriterRequestViewSet
from .views.orders.actions import OrderActionView
from orders.views.orders.transition_log import OrderTransitionLogListView
from .views.orders.order_request_viewset import OrderRequestViewSet
from orders.views.orders.order_deadline_view import ExtendOrderDeadlineView
from orders.views.orders.test_webhook_view import TestWebhookView
from orders.views.orders.webhook_preview_view import WebhookPreviewView
from orders.views.orders.retry_webhook_view import RetryWebhookView
from orders.views.orders.webhook_delivery_log_view import WebhookDeliveryLogListView
from orders.views.writers.writer_requests_preview import WriterRequestPreviewView
from orders.views.orders.editing_admin import OrderEditingAdminView
from orders.views.progress import WriterProgressViewSet


app_name = 'orders'
router = DefaultRouter()
router.register(r'orders', OrderBaseViewSet, basename='order')
router.register(r'disputes', DisputeViewSet, basename='dispute')
router.register(r'writer-request', WriterRequestViewSet, basename='writer-request')
router.register(r'order-requests', OrderRequestViewSet, basename='order-request')
router.register(
    r"reassignment-logs", WriterReassignmentLogViewSet, basename="reassignment-log"
)
router.register(r'progress', WriterProgressViewSet, basename='writer-progress')


urlpatterns = [
    path('', include(router.urls)),
    path('orders/<int:pk>/action/', OrderActionView.as_view(), name='order-action'),
    path("logs/", OrderTransitionLogListView.as_view(), name="order-transition-log-list"),
    path("logs/<int:pk>/", OrderTransitionLogListView.as_view(), name="order-transition-log-detail"),
    path('orders/<int:pk>/extend-deadline/', ExtendOrderDeadlineView.as_view(), name='extend-order-deadline'),
    # Back-compat name expected by tests
    path('orders/<int:pk>/extend-deadline/', ExtendOrderDeadlineView.as_view(), name='extend-deadline'),
    path('orders/<int:pk>/actions/', OrderActionView.as_view(), name='order-actions'),
    path(
        'orders/<int:pk>/actions/<str:action_name>/',
        OrderActionView.as_view(),
        name='order-action-detail'
    ),
    path(
        'orders/<int:pk>/actions/<str:action_name>/<str:action_type>/',
        OrderActionView.as_view(),
        name='order-action-type-detail'
    ),
    path(
        'orders/<int:pk>/actions/<str:action_name>/<str:action_type>/<str:action_subtype>/',
        OrderActionView.as_view(),
        name='order-action-subtype-detail'
    ),
    path(
        'orders/<int:pk>/actions/<str:action_name>/<str:action_type>/<str:action_subtype>/<str:action_target>/',
        OrderActionView.as_view(),
        name='order-action-target-detail'
    ),
    path("webhooks/test/", TestWebhookView.as_view(), name="webhook-test"),
    path(
        "webhooks/preview/<int:order_id>/",
        WebhookPreviewView.as_view(),
        name="webhook-preview"
    ),
    path(
        "webhooks/retry/<int:log_id>/",
        RetryWebhookView.as_view(),
        name="webhook-retry"
    ),
    path("admin/webhook-logs/", WebhookDeliveryLogListView.as_view()),
    path("admin/webhook-logs/<int:log_id>/retry/", RetryWebhookView.as_view()),

    path("writer-request/preview/", WriterRequestPreviewView.as_view(), name="writer-request-preview"),
    path(
        "admin/orders/<int:pk>/editing/",
        OrderEditingAdminView.as_view(),
        name="order-editing-admin"
    ),

]