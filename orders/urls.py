from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from .views import (
#     OrderViewSet,
#     DisputeViewSet,
#     OrderActionView
# )
from .views.orders.base import OrderViewSet
from .views.orders.disputes import DisputeViewSet
from .views.writers.writer_requests import WriterRequestViewSet
from .views.orders.actions import OrderActionViewSet

# Create a router and register the ViewSets
router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'disputes', DisputeViewSet, basename='dispute')
router.register(r'writer-request', WriterRequestViewSet, basename='writer-request')
router.register(r"actions", OrderActionViewSet, basename="order-action")

urlpatterns = [
    path('', include(router.urls)), # Include the router-generated URLs
]
