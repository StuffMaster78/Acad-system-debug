from django.urls import path
from authentication.views.sessions_management import (
    ActiveSessionsView, LogoutSessionView,
    LogoutAllSessionsView
)

urlpatterns = [
    path(
        'sessions/',
        ActiveSessionsView.as_view(),
        name='active-sessions'
    ),
    path(
        'sessions/logout/<int:session_id>/',
        LogoutSessionView.as_view(),
        name='logout-session'
    ),
    path(
        'sessions/logout/all/',
        LogoutAllSessionsView.as_view(),
        name='logout-all-sessions'
    ),
]