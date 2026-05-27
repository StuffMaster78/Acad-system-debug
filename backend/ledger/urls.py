from django.urls import include, path

app_name = "ledger"

urlpatterns = [
    path("", include("ledger.api.urls")),
]
