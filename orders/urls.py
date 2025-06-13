from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.orders.base import OrderBaseViewSet
from .views.orders.disputes import DisputeViewSet
from .views.writers.writer_requests import WriterRequestViewSet
from .views.orders.actions import OrderActionView

router = DefaultRouter()
router.register(r'orders', OrderBaseViewSet, basename='order')
router.register(r'disputes', DisputeViewSet, basename='dispute')
router.register(r'writer-request', WriterRequestViewSet, basename='writer-request')

urlpatterns = [
    path('', include(router.urls)),
    path('orders/<int:pk>/action/', OrderActionView.as_view(), name='order-action'),
]
