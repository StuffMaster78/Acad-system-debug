from django.urls import path
from .views import (
    UserProfileView,
    ListUsersView,
    WriterDetailView,
    EditorDetailView,
    SupportDetailView,
)

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('list/<str:role>/', ListUsersView.as_view(), name='list-users'),  # e.g., /list/client/, /list/writer/
    path('writers/<int:pk>/', WriterDetailView.as_view(), name='writer-detail'),
    path('editors/<int:pk>/', EditorDetailView.as_view(), name='editor-detail'),
    path('support/<int:pk>/', SupportDetailView.as_view(), name='support-detail'),
]