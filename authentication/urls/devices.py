from django.urls import path
from views.devices import (
    ListDevicesView,
    RevokeDeviceView,
    RenameDeviceView,
    DeleteDeviceView
)

urlpatterns = [
    path(
        '',
        ListDevicesView.as_view(),
        name='list-passkey-devices'
    ),
    path(
        '<int:credential_id>/',
        RevokeDeviceView.as_view(),
        name='revoke-passkey-device'
    ),
    path(
        "devices/<str:credential_id>/rename/",
        RenameDeviceView.as_view(),
        name="rename_device"
    ),
    path(
        "devices/<str:credential_id>/delete/",
        DeleteDeviceView.as_view(),
        name="delete_device"
    ),
]