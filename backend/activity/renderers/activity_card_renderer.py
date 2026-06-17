from __future__ import annotations

from typing import Any

from activity.models import ActivityEvent


class ActivityCardRenderer:
    """
    Converts activity events into frontend-friendly cards.

    Use render() for generic staff/admin feeds.
    Use render_for_viewer() for personalized client/writer feeds — it
    generates copy from the viewer's perspective so "You uploaded a file"
    vs "Your writer uploaded a file" vs "The client uploaded a file"
    are all derived from the same event record.
    """

    # ── Generic (viewer-blind) render ────────────────────────────────────────

    @staticmethod
    def render(event: ActivityEvent) -> dict[str, Any]:
        """Render an activity event into a feed card payload."""
        return {
            "id": str(event.id),
            "verb": event.verb,
            "severity": event.severity,
            "title": event.title,
            "summary": event.summary,
            "metadata": event.metadata,
            "occurred_at": event.occurred_at.isoformat(),
            "actor": ActivityCardRenderer._render_actor(event),
            "target": ActivityCardRenderer._render_target(event),
            "subject": ActivityCardRenderer._render_subject(event),
        }

    # ── Viewer-aware render ───────────────────────────────────────────────────

    @classmethod
    def render_for_viewer(
        cls,
        event: ActivityEvent,
        viewer_id: int | str | None,
        viewer_role: str | None,
    ) -> dict[str, Any]:
        """
        Render an activity event using copy personalised to the viewer.

        Examples
        --------
        Client views their own file upload:
            "You uploaded a file to Order #1042."
        Client views a writer file upload:
            "Your writer uploaded a file to Order #1042."
        Staff views the same writer upload:
            "Writer W-0042 uploaded a file to Order #1042."
        Client has an unanswered message:
            "You have an unanswered message on Order #1042."
        """
        base = cls.render(event)

        viewer_str = str(viewer_id) if viewer_id is not None else None
        actor_str = str(event.actor_object_id) if event.actor_object_id else None
        viewer_is_actor = viewer_str is not None and viewer_str == actor_str

        actor_type = getattr(event, "actor_type", None) or ""
        meta = event.metadata or {}

        title, summary, cta = cls._personalize(
            verb=event.verb,
            actor_type=actor_type,
            viewer_role=viewer_role or "",
            viewer_is_actor=viewer_is_actor,
            meta=meta,
            event=event,
        )

        base["title"] = title or base["title"]
        base["summary"] = summary or base["summary"]
        if cta:
            base["cta"] = cta
        base["viewer_is_actor"] = viewer_is_actor

        return base

    # ── Copy templates ────────────────────────────────────────────────────────

    @classmethod
    def _personalize(
        cls,
        *,
        verb: str,
        actor_type: str,
        viewer_role: str,
        viewer_is_actor: bool,
        meta: dict[str, Any],
        event: ActivityEvent,
    ) -> tuple[str, str, dict[str, Any] | None]:
        """
        Return (title, summary, cta) personalised for the viewer.
        Returns empty strings when no specific template matches — the
        caller falls back to the stored title/summary.
        """
        order_ref = cls._order_ref(meta, event)
        actor_label = cls._actor_label(actor_type, meta, viewer_role)

        # ── File events ────────────────────────────────────────────────────
        if verb == "file.uploaded":
            if viewer_is_actor:
                return (
                    f"You uploaded a file to {order_ref}.",
                    "Your file has been attached to the order.",
                    None,
                )
            if viewer_role == "client" and actor_type == "writer":
                return (
                    f"Your writer uploaded a file to {order_ref}.",
                    "A new file is available on your order.",
                    {"label": "View order", "path": cls._order_path(meta, viewer_role)},
                )
            if viewer_role in {"staff", "admin", "superadmin"}:
                return (
                    f"{actor_label} uploaded a file to {order_ref}.",
                    meta.get("file_purpose", "New file attached."),
                    None,
                )
            if viewer_role == "writer" and actor_type == "client":
                return (
                    f"The client added a file to {order_ref}.",
                    "A reference or instruction file was uploaded.",
                    {"label": "View order", "path": cls._order_path(meta, viewer_role)},
                )

        # ── Message events ─────────────────────────────────────────────────
        elif verb == "message.sent":
            if viewer_is_actor:
                return (
                    f"You sent a message on {order_ref}.",
                    "Your message has been delivered.",
                    None,
                )
            if viewer_role == "client" and actor_type == "writer":
                return (
                    f"Your writer sent a message on {order_ref}.",
                    "Check your order messages.",
                    {"label": "Reply", "path": cls._order_path(meta, viewer_role)},
                )
            if viewer_role == "writer" and actor_type == "client":
                return (
                    f"The client sent a message on {order_ref}.",
                    "A reply may be needed.",
                    {"label": "Reply", "path": cls._order_path(meta, viewer_role)},
                )
            if viewer_role in {"staff", "admin", "superadmin"}:
                return (
                    f"{actor_label} sent a message on {order_ref}.",
                    "",
                    None,
                )

        # ── Order submitted (writer delivers) ──────────────────────────────
        elif verb == "order.submitted":
            if viewer_is_actor:
                return (
                    f"You submitted {order_ref}.",
                    "The client will be notified to review the delivery.",
                    None,
                )
            if viewer_role == "client":
                return (
                    f"Your {order_ref} is ready for review.",
                    "Download and review the delivery. Request revisions if needed.",
                    {"label": "Review delivery", "path": cls._order_path(meta, viewer_role)},
                )
            if viewer_role in {"staff", "admin", "superadmin"}:
                return (
                    f"{actor_label} submitted {order_ref}.",
                    "Awaiting client approval or QA review.",
                    None,
                )

        # ── Order created ──────────────────────────────────────────────────
        elif verb == "order.created":
            if viewer_is_actor:
                return (
                    f"You placed {order_ref}.",
                    "Your order is in queue. We'll match you with a writer shortly.",
                    None,
                )
            if viewer_role in {"staff", "admin", "superadmin"}:
                return (
                    f"{actor_label} placed {order_ref}.",
                    "",
                    None,
                )

        # ── Order assigned ─────────────────────────────────────────────────
        elif verb == "order.assigned":
            if viewer_role == "client":
                return (
                    f"A writer has been assigned to {order_ref}.",
                    "Work has begun. You can message your writer directly.",
                    {"label": "Message writer", "path": cls._order_path(meta, viewer_role)},
                )
            if viewer_role == "writer" and viewer_is_actor:
                return (
                    f"You were assigned {order_ref}.",
                    "Review the brief and begin work by the deadline.",
                    {"label": "View order", "path": cls._order_path(meta, viewer_role)},
                )
            if viewer_role in {"staff", "admin", "superadmin"}:
                return (
                    f"{actor_label} was assigned to {order_ref}.",
                    "",
                    None,
                )

        # ── Order completed ────────────────────────────────────────────────
        elif verb == "order.completed":
            if viewer_role == "client":
                return (
                    f"{order_ref} has been completed.",
                    "Thank you for using ResearchPaperMate. Please leave a review.",
                    {"label": "Leave a review", "path": cls._order_path(meta, viewer_role)},
                )
            if viewer_role == "writer":
                return (
                    f"{order_ref} marked as completed.",
                    "Your earnings have been posted to your wallet.",
                    None,
                )

        # ── Revision requested ─────────────────────────────────────────────
        elif verb == "order.revision_requested":
            if viewer_role == "writer":
                return (
                    f"A revision was requested on {order_ref}.",
                    "Review the client's feedback and resubmit within the revision window.",
                    {"label": "View revision request", "path": cls._order_path(meta, viewer_role)},
                )
            if viewer_role == "client" and viewer_is_actor:
                return (
                    f"You requested a revision on {order_ref}.",
                    "Your writer has been notified.",
                    None,
                )
            if viewer_role in {"staff", "admin", "superadmin"}:
                return (
                    f"Revision requested on {order_ref}.",
                    "",
                    None,
                )

        # ── Wallet events ──────────────────────────────────────────────────
        elif verb == "wallet.credited":
            amount = meta.get("amount", "")
            return (
                f"Your wallet was credited{f' with {amount}' if amount else ''}.",
                "",
                None,
            )
        elif verb == "wallet.debited":
            amount = meta.get("amount", "")
            return (
                f"{'Your' if viewer_is_actor else 'A'} wallet deduction of {amount} was applied.",
                "",
                None,
            )

        # ── Payment received ───────────────────────────────────────────────
        elif verb == "payment.received":
            amount = meta.get("amount", "")
            if viewer_role == "client" and viewer_is_actor:
                return (
                    f"Payment of {amount} received for {order_ref}.",
                    "Your order is now fully paid and in progress.",
                    None,
                )
            if viewer_role in {"staff", "admin", "superadmin"}:
                return (
                    f"Payment of {amount} received on {order_ref}.",
                    "",
                    None,
                )

        # No specific template — caller uses stored title/summary
        return "", "", None

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _order_ref(meta: dict[str, Any], event: ActivityEvent) -> str:
        """Return a human-readable order reference."""
        order_id = (
            meta.get("order_id")
            or meta.get("order")
            or getattr(event, "target_object_id", None)
        )
        if order_id:
            return f"Order #{order_id}"
        return "your order"

    @staticmethod
    def _order_path(meta: dict[str, Any], viewer_role: str) -> str:
        """Return the portal path to the order detail page."""
        order_id = meta.get("order_id") or meta.get("order")
        if not order_id:
            return "/orders"
        role_prefix = {
            "client": "/client",
            "writer": "/writer",
            "staff": "/admin",
            "admin": "/admin",
            "superadmin": "/superadmin",
        }.get(viewer_role, "/admin")
        return f"{role_prefix}/orders/{order_id}"

    @staticmethod
    def _actor_label(actor_type: str, meta: dict[str, Any], viewer_role: str) -> str:
        """Return a display-safe label for the actor."""
        name = meta.get("actor_name") or meta.get("actor_username") or ""
        if name:
            return name
        labels = {
            "client": "The client",
            "writer": "The writer",
            "staff": "A staff member",
            "admin": "An admin",
            "superadmin": "Superadmin",
            "system": "The system",
        }
        return labels.get(actor_type, "A user")

    @staticmethod
    def _render_actor(event: ActivityEvent) -> dict[str, Any] | None:
        actor = event.actor
        content_type = event.actor_content_type
        if actor is None or content_type is None:
            return None
        return {
            "type": content_type.model,
            "id": event.actor_object_id,
            "label": str(actor),
        }

    @staticmethod
    def _render_target(event: ActivityEvent) -> dict[str, Any]:
        return {
            "type": event.target_content_type.model,
            "id": event.target_object_id,
            "label": str(event.target),
        }

    @staticmethod
    def _render_subject(event: ActivityEvent) -> dict[str, Any] | None:
        subject = event.subject
        content_type = event.subject_content_type
        if subject is None or content_type is None:
            return None
        return {
            "type": content_type.model,
            "id": event.subject_object_id,
            "label": str(subject),
        }
