from django.urls import path

from cms_service_pages.views import ServicePageSchemaView

app_name = "cms_service_pages"

urlpatterns = [
    path("schema/<int:page_id>/", ServicePageSchemaView.as_view(), name="service-schema"),
]
