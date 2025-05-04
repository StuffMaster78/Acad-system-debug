from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderViewSet,
    DisputeViewSet,
    OrderActionView
)

# Create a router and register the ViewSets
router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'disputes', DisputeViewSet, basename='dispute')

urlpatterns = [
    path('', include(router.urls)), # Include the router-generated URLs
    path('<int:pk>/action/', OrderActionView.as_view(), name='order-action'),
]
