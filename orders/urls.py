from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet
from orders.views import (
    PaymentTransactionListView,
    PaymentTransactionDetailView,
    PaymentTransactionCreateView,
    PaymentTransactionUpdateView,
    PaymentTransactionDeleteView,
)
# Create a router and register the OrderViewSet
router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    # Include the routes from the router
    path('', include(router.urls)),
    path("transactions/", PaymentTransactionListView.as_view(), name="transaction-list"),
    path("transactions/<int:pk>/", PaymentTransactionDetailView.as_view(), name="transaction-detail"),
    path("transactions/create/", PaymentTransactionCreateView.as_view(), name="transaction-create"),
    path("transactions/update/<int:pk>/", PaymentTransactionUpdateView.as_view(), name="transaction-update"),
    path("transactions/delete/<int:pk>/", PaymentTransactionDeleteView.as_view(), name="transaction-delete"),
]