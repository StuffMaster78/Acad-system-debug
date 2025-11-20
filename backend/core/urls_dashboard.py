"""
URLs for dashboard configuration endpoints
"""
from django.urls import path
from core.views.dashboard_config import DashboardConfigView

urlpatterns = [
    path('', DashboardConfigView.as_view(), name='dashboard-config'),
]

