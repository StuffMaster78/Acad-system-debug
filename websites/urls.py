from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WebsiteViewSet

# Initialize the router and register the WebsiteViewSet
router = DefaultRouter()
router.register(r'', WebsiteViewSet, basename='website')

# Define urlpatterns for the app
urlpatterns = [
    path('websites/', include(router.urls)),  # Prefix the routes with 'websites/'
]