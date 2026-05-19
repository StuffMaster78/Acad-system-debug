from django.urls import include, path

urlpatterns = [
    path(
        "",
        include("files_management.api.urls"),
    ),
]
