from django.urls import path
from .views import SavedViewDetailView, SavedViewListView

urlpatterns = [
    path("", SavedViewListView.as_view(), name="saved-views-list"),
    path("<int:pk>/", SavedViewDetailView.as_view(), name="saved-views-detail"),
]
