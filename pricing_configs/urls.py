from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PricingConfigurationViewSet,
    AdditionalServiceViewSet,
    AcademicLevelPricingViewSet,
    TypeOfWorkMultiplierViewSet,
    DeadlineMultiplierViewSet,
    PreferredWriterConfigViewSet,
    WriterLevelOptionConfigViewSet,
    EstimatePriceView
)

router = DefaultRouter()
router.register(r'pricing-configurations', PricingConfigurationViewSet)
router.register(r'additional-services', AdditionalServiceViewSet)
router.register(r'academic-level-pricing', AcademicLevelPricingViewSet)
router.register(r'type-of-work-multipliers', TypeOfWorkMultiplierViewSet)
router.register(r'deadline-multipliers', DeadlineMultiplierViewSet)
router.register(r'preferred-writer-configs', PreferredWriterConfigViewSet)
router.register(r'writer-level-options', WriterLevelOptionConfigViewSet)

urlpatterns = [
    path('estimate/', EstimatePriceView.as_view(), name='estimate-price'),
    path('', include(router.urls)),
]
