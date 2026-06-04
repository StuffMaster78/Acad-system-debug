from django.urls import path
from .views import ChangelogListView

urlpatterns = [
    path("", ChangelogListView.as_view(), name="changelog-list"),
]
