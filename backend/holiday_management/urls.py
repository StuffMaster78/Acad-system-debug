"""
Holiday Management URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SpecialDayViewSet,
    HolidayReminderViewSet,
    HolidayDiscountCampaignViewSet
)

router = DefaultRouter()
router.register(r'special-days', SpecialDayViewSet, basename='special-day')
router.register(r'reminders', HolidayReminderViewSet, basename='holiday-reminder')
router.register(r'campaigns', HolidayDiscountCampaignViewSet, basename='holiday-campaign')

urlpatterns = [
    path('', include(router.urls)),
]

