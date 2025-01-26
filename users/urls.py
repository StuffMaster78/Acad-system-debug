from django.urls import path
from .views import (
    UserProfileView, 
    ClientListView, 
    WriterListView,
    WriterDetailView, 
    EditorListView, 
    SupportListView,
)

urlpatterns = [
    # Profile-related endpoints
    path('profile/', UserProfileView.as_view(), name='user-profile'),  # View profile for the logged-in user

    # Role-specific endpoints
    path('clients/', ClientListView.as_view(), name='client-list'),  # List all clients (admin-only)
    path('writers/', WriterListView.as_view(), name='writer-list'),  # List all writers (admin-only)
    path('writers/<int:pk>/', WriterDetailView.as_view(), name='writer-detail'),  # Retrieve or update a specific writer (admin-only)
    path('editors/', EditorListView.as_view(), name='editor-list'),  # List all editors (admin-only)
    path('support/', SupportListView.as_view(), name='support-list'),  # List all support staff (admin-only)
]
