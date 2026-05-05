from __future__ import annotations

from string import Template

from communications.models.saved_reply import CommunicationSavedReply


class CommunicationSavedReplyService:
    """
    Manage reusable support reply templates.
    """

    @staticmethod
    def create(
        *,
        website,
        title: str,
        body: str,
        category: str = "",
        created_by=None,
    ) -> CommunicationSavedReply:
        """
        Create a saved reply.
        """
        return CommunicationSavedReply.objects.create(
            website=website,
            title=title,
            body=body,
            category=category,
            created_by=created_by,
        )

    @staticmethod
    def update(
        *,
        saved_reply,
        title: str | None = None,
        body: str | None = None,
        category: str | None = None,
        is_active: bool | None = None,
    ) -> CommunicationSavedReply:
        """
        Update a saved reply.
        """
        update_fields: list[str] = []

        if title is not None:
            saved_reply.title = title
            update_fields.append("title")

        if body is not None:
            saved_reply.body = body
            update_fields.append("body")

        if category is not None:
            saved_reply.category = category
            update_fields.append("category")

        if is_active is not None:
            saved_reply.is_active = is_active
            update_fields.append("is_active")

        if update_fields:
            update_fields.append("updated_at")
            saved_reply.save(update_fields=update_fields)

        return saved_reply

    @staticmethod
    def render(
        *,
        saved_reply,
        context: dict[str, object] | None = None,
    ) -> str:
        """
        Render a saved reply using safe template substitution.
        """
        template = Template(saved_reply.body)
        return template.safe_substitute(context or {})