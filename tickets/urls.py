from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TicketViewSet, TicketMessageViewSet,
    TicketLogViewSet, TicketStatisticsViewSet,
    TicketAttachmentViewSet
)

router = DefaultRouter()
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'messages', TicketMessageViewSet, basename='ticket-message')
router.register(r'logs', TicketLogViewSet, basename='ticket-log')
router.register(r'statistics', TicketStatisticsViewSet, basename='ticket-statistics')
router.register(r'attachments', TicketAttachmentViewSet, basename='ticket-attachment')

urlpatterns = [
    path('', include(router.urls)),
]