from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView
from .swagger import SecureSwaggerView, SecureRedocView

router = DefaultRouter()
router.register(r'service-pages', ServicePageViewSet, basename='service-pages')

urlpatterns = [
    # Core API
    path('', include(router.urls)),


    # Schema endpoint
    path('schema/', SpectacularAPIView.as_view(), name='schema'),

    # Secure Swagger UI
    path(
        'docs/swagger/',
        SecureSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),

    # Secure Redoc UI
    path(
        'docs/redoc/',
        SecureRedocView.as_view(url_name='schema'),
        name='redoc'
    ),
]