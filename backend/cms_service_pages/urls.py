from django.urls import path

from cms_service_pages.views import (
    ServicePageBySlugView,
    ServicePageListView,
    ServicePageSchemaView,
)

app_name = "cms_service_pages"

urlpatterns = [
    path("", ServicePageListView.as_view(), name="service-list"),
    path("by-slug/<slug:slug>/", ServicePageBySlugView.as_view(), name="service-by-slug"),
    path("schema/<int:page_id>/", ServicePageSchemaView.as_view(), name="service-schema"),
]
