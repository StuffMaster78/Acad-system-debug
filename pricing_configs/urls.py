from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PricingConfigurationViewSet, AdditionalServiceViewSet, WriterQualityViewSet

# Create a router and register the viewsets
router = DefaultRouter()
router.register(r'pricing-configurations', PricingConfigurationViewSet, basename='pricing-configuration')
router.register(r'additional-services', AdditionalServiceViewSet, basename='additional-service')
router.register(r'writer-qualities', WriterQualityViewSet, basename='writer-quality')

urlpatterns = [
    path('', include(router.urls)),  # Include all API endpoints from the router
]