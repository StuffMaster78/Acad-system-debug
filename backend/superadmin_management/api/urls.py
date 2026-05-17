from django.urls import path

from superadmin_management.api.views.approvals_views import ApprovalViewSet
from superadmin_management.api.views.policy_views import PolicyViewSet
from superadmin_management.api.views.command_views import CommandViewSet
from superadmin_management.api.views.replay_views import CommandReplayView


urlpatterns = [
    # approvals
    path("approvals/", ApprovalViewSet.as_view({"get": "list"})),
    path("approvals/<uuid:pk>/", ApprovalViewSet.as_view({"get": "retrieve"})),
    path("approvals/<uuid:pk>/approve/", ApprovalViewSet.as_view({"post": "approve"})),
    path("approvals/<uuid:pk>/reject/", ApprovalViewSet.as_view({"post": "reject"})),

    # policies (graph editor)
    path("policies/", PolicyViewSet.as_view({"get": "list", "post": "create"})),
    path("policies/<uuid:pk>/", PolicyViewSet.as_view({"get": "retrieve", "patch": "update"})),

    # commands
    path("commands/", CommandViewSet.as_view({"get": "list"})),
    path("commands/<uuid:pk>/", CommandViewSet.as_view({"get": "retrieve"})),

    # replay / time travel
    path("commands/<uuid:pk>/replay/", CommandReplayView.as_view()),
]