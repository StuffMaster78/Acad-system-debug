from django.urls import path, include
from rest_framework.routers import DefaultRouter
from fines.views import FineViewSet, FineAppealViewSet
from fines.views.lateness_rule_views import LatenessFineRuleViewSet, FineTypeConfigViewSet

router = DefaultRouter()
router.register(r"fines", FineViewSet, basename="fine")
router.register(r"fine-appeals", FineAppealViewSet, basename="fine-appeal")
router.register(r"lateness-rules", LatenessFineRuleViewSet, basename="lateness-fine-rule")
router.register(r"fine-types", FineTypeConfigViewSet, basename="fine-type-config")

urlpatterns = [
    path('api/', include(router.urls)),
]