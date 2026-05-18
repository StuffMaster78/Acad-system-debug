from django.urls import include, path

urlpatterns = [
    path("", include("tips.api.urls")),
    path("admin/", include("tips.api.admin_urls")),
]