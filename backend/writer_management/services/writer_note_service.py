"""
Owns all mutations to WriterNote.

Simple service — notes are append-friendly with minimal
lifecycle. The main concerns are:
    - Permission checking (done in views/serializers, not here)
    - Audit logging (WriterActivityLog for admin actions)
    - Pin/unpin toggle
"""

import logging

from django.db import transaction

from writer_management.models.writer_note import WriterNote

logger = logging.getLogger(__name__)


class WriterNoteService:

    @staticmethod
    @transaction.atomic
    def create_note(
        writer,
        website,
        created_by,
        note: str,
        is_pinned: bool = False,
        is_sensitive: bool = False,
        related_order_id: int | None = None,
    ) -> WriterNote:
        """
        Create an internal admin note on a writer.

        Args:
            writer: WriterProfile instance.
            website: Website instance.
            created_by: Admin User writing the note.
            note: Note content.
            is_pinned: Pin to top of note history.
            is_sensitive: Flag as requiring elevated permissions.
            related_order_id: Optional order PK for context.

        Returns:
            Created WriterNote instance.

        Raises:
            ValueError: If note content is blank.
        """
        if not note.strip():
            raise ValueError("Note content cannot be blank.")

        writer_note = WriterNote.objects.create(
            website=website,
            writer=writer,
            created_by=created_by,
            note=note.strip(),
            is_pinned=is_pinned,
            is_sensitive=is_sensitive,
            related_order_id=related_order_id,
        )

        logger.info(
            "WriterNote created: writer=%s note=%s by=%s pinned=%s sensitive=%s",
            writer.registration_id,
            writer_note.pk,
            getattr(created_by, "pk", "system"),
            is_pinned,
            is_sensitive,
        )

        return writer_note

    @staticmethod
    @transaction.atomic
    def update_note(
        note: WriterNote,
        updated_by,
        new_content: str | None = None,
        is_pinned: bool | None = None,
        is_sensitive: bool | None = None,
    ) -> WriterNote:
        """
        Update a writer note's content or flags.

        Only the fields explicitly passed are updated.

        Args:
            note:        WriterNote instance to update.
            updated_by:  Admin User making the change.
            new_content: New note text. None = no change.
            is_pinned:   New pin state. None = no change.
            is_sensitive: New sensitivity flag. None = no change.

        Returns:
            Updated WriterNote instance.
        """
        update_fields = ["updated_at"]

        if new_content is not None:
            if not new_content.strip():
                raise ValueError("Note content cannot be blank.")
            note.note = new_content.strip()
            update_fields.append("note")

        if is_pinned is not None:
            note.is_pinned = is_pinned
            update_fields.append("is_pinned")

        if is_sensitive is not None:
            note.is_sensitive = is_sensitive
            update_fields.append("is_sensitive")

        note.save(update_fields=update_fields)

        logger.info(
            "WriterNote updated: note=%s writer=%s by=%s fields=%s",
            note.pk,
            note.writer.pk,
            getattr(updated_by, "pk", "system"),
            update_fields,
        )

        return note

    @staticmethod
    @transaction.atomic
    def delete_note(note: WriterNote, deleted_by) -> None:
        """
        Delete a writer note.

        Notes are deletable — they are not formal discipline records.
        Sensitive notes should require elevated permissions (enforced
        in the view layer, not here).

        Args:
            note:       WriterNote instance to delete.
            deleted_by: Admin User performing the deletion.
        """
        writer_id = note.writer.pk
        note_pk = note.pk

        note.delete()

        logger.info(
            "WriterNote deleted: note=%s writer=%s by=%s",
            note_pk,
            writer_id,
            getattr(deleted_by, "pk", "system"),
        )

    @staticmethod
    def toggle_pin(note: WriterNote, toggled_by) -> WriterNote:
        """Toggle the pinned state of a note."""
        return WriterNoteService.update_note(
            note=note,
            updated_by=toggled_by,
            is_pinned=not note.is_pinned,
        )

    @staticmethod
    def get_notes_for_writer(writer, include_sensitive: bool = False):
        """
        Return notes for a writer ordered by pin then recency.

        Args:
            writer: WriterProfile instance.
            include_sensitive: If False, excludes sensitive notes.
                               Pass True only for elevated admin roles.

        Returns:
            WriterNote queryset.
        """
        qs = WriterNote.objects.filter(
            writer=writer,
        ).select_related("created_by").order_by("-is_pinned", "-created_at")

        if not include_sensitive:
            qs = qs.filter(is_sensitive=False)

        return qs