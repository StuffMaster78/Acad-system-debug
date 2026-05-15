from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.db.models import QuerySet

from writer_management.services.writer_note_service import WriterNoteService
from writer_management.models.writer_note import WriterNote
from writer_management.api.permissions import IsAdminUser, _resolve_website


class WriterNoteListView(ListAPIView):
    """GET /api/writer-management/writers/<rid>/notes/"""
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):  # type: ignore[override]
        from writer_management.api.serializers.note_serializers import (
            WriterNoteSerializer,
        )
        return WriterNoteSerializer

    def get_queryset(self) -> QuerySet:  # type: ignore[override]
        from writer_management.services.writer_profile_service import (
            WriterProfileService,
        )
        rid = self.kwargs["registration_id"]

        # Fix 1: use self.request.GET — HttpRequest always has .GET
        # .query_params is DRF-only and not in the HttpRequest stubs
        include_sensitive = self.request.GET.get(
            "include_sensitive", "false"
        ).lower() == "true"

        try:
            writer = WriterProfileService.get_by_registration_id(rid)
        except Exception:
            return WriterNote.objects.none()

        return WriterNoteService.get_notes_for_writer(
            writer=writer,
            include_sensitive=include_sensitive,
        )


class CreateWriterNoteView(APIView):
    """POST /api/writer-management/writers/<rid>/notes/"""
    permission_classes = [IsAdminUser]

    def post(self, request, registration_id):
        from writer_management.api.serializers.note_serializers import (
            CreateWriterNoteSerializer,
            WriterNoteSerializer,
        )
        from writer_management.services.writer_profile_service import (
            WriterProfileService,
        )

        try:
            writer = WriterProfileService.get_by_registration_id(
                registration_id
            )
        except Exception:
            return Response({"detail": "Writer not found."}, status=404)

        serializer = CreateWriterNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Fix 2: was `note=note` — circular reference (note not yet assigned).
        # Fix 3: was **d — Pylance rejects validated_data as ** mapping.
        # Solution: explicit keyword arguments from the validated data dict.
        d: dict = serializer.validated_data  # type: ignore[assignment]
        website = _resolve_website(request)

        note_obj = WriterNoteService.create_note(
            writer=writer,
            website=website,
            created_by=request.user,
            note=d["note"],
            is_pinned=d.get("is_pinned", False),
            is_sensitive=d.get("is_sensitive", False),
            related_order_id=d.get("related_order_id"),
        )
        return Response(
            WriterNoteSerializer(note_obj).data,
            status=status.HTTP_201_CREATED,
        )


class UpdateWriterNoteView(APIView):
    """
    PATCH  /api/writer-management/notes/<pk>/
    DELETE /api/writer-management/notes/<pk>/
    """
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        from writer_management.api.serializers.note_serializers import (
            UpdateWriterNoteSerializer,
            WriterNoteSerializer,
        )

        try:
            note_obj = WriterNote.objects.get(pk=pk)
        except WriterNote.DoesNotExist:
            return Response({"detail": "Note not found."}, status=404)

        serializer = UpdateWriterNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Fix 4: validated_data typed as `empty` before is_valid() in stubs.
        # Cast to dict so .get() is available without Pylance complaints.
        d: dict = serializer.validated_data  # type: ignore[assignment]

        updated = WriterNoteService.update_note(
            note=note_obj,
            updated_by=request.user,
            new_content=d.get("note"),
            is_pinned=d.get("is_pinned"),
            is_sensitive=d.get("is_sensitive"),
        )
        return Response(WriterNoteSerializer(updated).data)

    def delete(self, request, pk):
        try:
            note_obj = WriterNote.objects.get(pk=pk)
        except WriterNote.DoesNotExist:
            return Response({"detail": "Note not found."}, status=404)

        WriterNoteService.delete_note(
            note=note_obj,
            deleted_by=request.user,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class TogglePinNoteView(APIView):
    """POST /api/writer-management/notes/<pk>/pin/"""
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            note_obj = WriterNote.objects.get(pk=pk)
        except WriterNote.DoesNotExist:
            return Response({"detail": "Note not found."}, status=404)

        WriterNoteService.toggle_pin(
            note=note_obj,
            toggled_by=request.user,
        )
        return Response({
            "detail": "Pin toggled.",
            "is_pinned": note_obj.is_pinned,
        })