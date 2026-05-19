from .frontend_url import (
    build_frontend_url_for_user,
    get_frontend_base_url_for_user,
    get_login_url,
    get_profile_edit_url,
    get_profile_url,
    get_security_settings_url,
    get_settings_url,
)
from django.urls import path

from core.views.dropdown_options import (
    DropdownOptionsByCategoryView,
    DropdownOptionsView,
)

urlpatterns = [
    path("", DropdownOptionsView.as_view(), name="dropdown-options"),
    path(
        "<str:category>/",
        DropdownOptionsByCategoryView.as_view(),
        name="dropdown-options-category",
    ),
]

__all__ = [
    "build_frontend_url_for_user",
    "get_frontend_base_url_for_user",
    "get_login_url",
    "get_profile_edit_url",
    "get_profile_url",
    "get_security_settings_url",
    "get_settings_url",
    "urlpatterns",
]
