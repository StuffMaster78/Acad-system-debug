from django.urls import path
from authentication.views.account import (
    RegisterView,
    ActivationView,
    FinalizeAccountView
)

urlpatterns = [
    path(
        'register/',
        RegisterView.as_view(),
        name='register'
    ),
    path(
        'activate/<str:token>/',
        ActivationView.as_view(),
        name='activate-account'
    ),
    path(
        'finalize-account/',
        FinalizeAccountView.as_view(),
        name='finalize-account'
    ),
]