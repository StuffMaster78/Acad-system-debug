from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WriterPaymentManagementViewSet

router = DefaultRouter()
router.register('payment-management', WriterPaymentManagementViewSet, basename='payment-management')

urlpatterns = [
    path('', include(router.urls)),
]

