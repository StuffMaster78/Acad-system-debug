from django.urls import path, include
from rest_framework.routers import DefaultRouter
from class_management.views import (
    ClassPurchaseViewSet, ClassInstallmentViewSet, ClassBundleConfigViewSet,
    ClassBundleViewSet
)

# Initialize the router
router = DefaultRouter()

# Register the viewsets with the router
router.register(r'class-bundles', ClassBundleViewSet, basename='class-bundle')
router.register(r'class-purchases', ClassPurchaseViewSet, basename='class-purchase')
router.register(r'class-installments', ClassInstallmentViewSet, basename='class-installment')
router.register(r'class-bundle-configs', ClassBundleConfigViewSet, basename='class-bundle-config')

urlpatterns = [
    path('', include(router.urls)),  # Include all the generated routes from the router
]