from django.urls import include, path

urlpatterns = [
    path("", include("files_management.api.urls.urls")),
    path("admin/", include("files_management.api.urls.admin_urls")),
]
