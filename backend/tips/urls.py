from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("api/v1/tips/", include("tips.api.urls")),
    path("api/v1/admin/tips/", include("tips.api.admin_urls")),
]