from django.urls import path, include

urlpatterns = [
    path("api/", include("reviews_system.api.urls")),
]