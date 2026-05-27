from django.urls import include, path

app_name = "discounts"

urlpatterns = [
    path("", include("discounts.api.urls")),
]
