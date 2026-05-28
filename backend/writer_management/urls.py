from django.urls import include, path

app_name = "writer_management"

urlpatterns = [
    path("", include("writer_management.api.urls")),
]
