from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PredefinedSpecialOrderConfigViewSet, SpecialOrderViewSet, MilestoneViewSet, ProgressLogViewSet, WriterBonusViewSet
)

router = DefaultRouter()
router.register('predefined-configs', PredefinedSpecialOrderConfigViewSet)
router.register('special-orders', SpecialOrderViewSet)
router.register('milestones', MilestoneViewSet)
router.register('progress-logs', ProgressLogViewSet)
router.register('writer-bonuses', WriterBonusViewSet)

urlpatterns = [
    path('', include(router.urls)),
]