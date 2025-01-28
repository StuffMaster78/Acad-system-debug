from rest_framework.routers import DefaultRouter
from .views import TicketViewSet, TicketMessageViewSet

router = DefaultRouter()
router.register(r'tickets', TicketViewSet, basename='tickets')
router.register(r'messages', TicketMessageViewSet, basename='ticket-messages')

urlpatterns = router.urls