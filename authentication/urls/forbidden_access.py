from django.urls import path
from authentication.views.forbidden_access import ForbiddenAccessView

urlpatterns = [
    path(
        "auth/forbidden/",
        ForbiddenAccessView.as_view(),
        name="forbidden-access"
    ),
]