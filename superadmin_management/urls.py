from django.urls import path
from .views import SuperadminProfileViewSet, UserManagementViewSet, SuperadminLogViewSet
from .views import superadmin_dashboard

urlpatterns = [
    path('superadmin-profile/', SuperadminProfileViewSet.as_view({'get': 'list'})),
    path('users/', UserManagementViewSet.as_view({'get': 'list_users', 'post': 'create_user'})),
    path('suspend-user/', UserManagementViewSet.as_view({'post': 'suspend_user'})),
    path('reactivate-user/', UserManagementViewSet.as_view({'post': 'reactivate_user'})),
    path('change-role/', UserManagementViewSet.as_view({'post': 'change_user_role'})),
    path('logs/', SuperadminLogViewSet.as_view({'get': 'list'})),
    path("dashboard/", superadmin_dashboard, name="superadmin_dashboard"),
]