from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PricingConfigurationViewSet, AdditionalServiceViewSet

# Create a router and register the viewsets
router = DefaultRouter()
router.register(r'pricing-configurations', PricingConfigurationViewSet, basename='pricing-configuration')
router.register(r'additional-services', AdditionalServiceViewSet, basename='additional-service')

urlpatterns = [
    path('', include(router.urls)),  # Include all API endpoints from the router
]