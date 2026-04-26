from django.urls import include, path

urlpatterns = [
    path(
        "api/files/",
        include("files_management.api.urls"),
    ),
    path(
        "api/admin/files/",
        include("files_management.api.admin_urls"),
    ),
]