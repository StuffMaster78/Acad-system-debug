from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)
from .views import (
    ServicePageViewSet,
    ServicePageCategoryViewSet,
)

router = DefaultRouter()
router.register(r'service-pages', ServicePageViewSet)
router.register(r'service-categories', ServicePageCategoryViewSet)

urlpatterns = [
    # Core API
    path('', include(router.urls)),

    # OpenAPI schema
    path('schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI
    path(
        'docs/swagger/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),

    # Redoc
    path(
        'docs/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc'
    ),
]