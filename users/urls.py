from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

# Initialize the router and register the viewset
router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')  # Simplified URL path for cleaner routing

# Define urlpatterns for the app
urlpatterns = [
    path('users/', include(router.urls)),  # Prefix the app's routes with 'users/'
]