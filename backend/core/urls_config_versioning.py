"""
URLs for configuration versioning.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views.config_versioning import ConfigVersioningViewSet

router = DefaultRouter()
router.register(r'', ConfigVersioningViewSet, basename='config-versioning')

urlpatterns = [
    path('', include(router.urls)),
]

