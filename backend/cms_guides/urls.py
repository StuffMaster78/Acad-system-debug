from django.urls import path

from .views import GuideDetailView, GuideListView

urlpatterns = [
    path("",          GuideListView.as_view(),   name="guide-list"),
    path("<slug:slug>/", GuideDetailView.as_view(), name="guide-detail"),
]
