"""
Analytics URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClientAnalyticsViewSet,
    WriterAnalyticsViewSet,
    ClassAnalyticsViewSet
)

router = DefaultRouter()
router.register(r'client', ClientAnalyticsViewSet, basename='client-analytics')
router.register(r'writer', WriterAnalyticsViewSet, basename='writer-analytics')
router.register(r'class', ClassAnalyticsViewSet, basename='class-analytics')

urlpatterns = [
    path('', include(router.urls)),
]

