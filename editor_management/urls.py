from django.urls import path
from . import views

urlpatterns = [
    path("profile/", views.EditorProfileDetailView.as_view(), name="editor-profile"),
    path("tasks/", views.EditorTaskListView.as_view(), name="editor-tasks"),
    path("performance/", views.EditorPerformanceView.as_view(), name="editor-performance"),
    path("notifications/", views.EditorNotificationsView.as_view(), name="editor-notifications"),
]