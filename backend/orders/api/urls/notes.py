from __future__ import annotations

from django.urls import path

from orders.api.views.notes.notes_views import OrderNoteDetailView, OrderNotesView

urlpatterns = [
    path(
        "orders/<int:order_id>/notes/",
        OrderNotesView.as_view(),
        name="order-notes-list",
    ),
    path(
        "orders/<int:order_id>/notes/<int:note_id>/",
        OrderNoteDetailView.as_view(),
        name="order-note-detail",
    ),
]
