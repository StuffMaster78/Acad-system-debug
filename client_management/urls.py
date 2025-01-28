from django.urls import path
from . import views

urlpatterns = [
    path("clients/", views.ClientProfileListCreateView.as_view(), name="client-list"),
    path("clients/<int:pk>/", views.ClientProfileDetailView.as_view(), name="client-detail"),
    path("clients/<int:client_id>/wallet/", views.ClientWalletView.as_view(), name="client-wallet"),
    path("clients/<int:client_id>/actions/", views.ClientActionView.as_view(), name="client-actions"),
    # Non-Critical Fields
    path("self/edit/", views.ClientProfileEditView.as_view(), name="client-profile-edit"),
    # Critical Fields (Request-Based)
    path("profile-update-requests/", views.ProfileUpdateRequestCreateView.as_view(), name="create-profile-update-request"),
    path("profile-update-requests/admin/", views.ProfileUpdateRequestListView.as_view(), name="list-profile-update-requests"),
]