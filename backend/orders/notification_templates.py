from __future__ import annotations

"""Class-based order templates bound to canonical event keys.

Each template reads from the enriched context produced by
``build_order_context``. That context has keys like:
  - presentation.subject, presentation.preheader, presentation.cta_text
  - order.number, order.status, order.time_left
  - client/email, writer/email (minimal safe fields)
  - urls.order / approve / rate / upload, etc.

Return (title, text, html) from ``render``.
"""

from typing import Dict, Tuple

from notifications_system.registry.template_registry import (
    register_template,
    register_template_name,
    BaseNotificationTemplate,
)


def _title(ctx: Dict, default: str) -> str:
    """Pick a good title from context with a fallback."""
    pres = ctx.get("presentation", {})
    return pres.get("subject") or default


def _preheader(ctx: Dict, default: str) -> str:
    """Pick a preheader/preview text from context with a fallback."""
    pres = ctx.get("presentation", {})
    return pres.get("preheader") or default


def _cta(ctx: Dict) -> Tuple[str, str]:
    """Return (cta_text, cta_url) from context with safe defaults."""
    pres = ctx.get("presentation", {})
    return pres.get("cta_text", "Open"), pres.get("cta_url", "")


def _order_num(ctx: Dict) -> str:
    """Formatted order number for copy convenience."""
    num = (ctx.get("order") or {}).get("number") or ""
    return f" #{num}" if num else ""


def _html(title: str, body: str, cta_text: str, cta_url: str) -> str:
    """Very small HTML stub suitable for email/push fallbacks."""
    cta = f'<p><a href="{cta_url}">{cta_text}</a></p>' if cta_url else ""
    return (
        f"<h3>{title}</h3>"
        f"<p>{body}</p>"
        f"{cta}"
    )


@register_template("order.assigned")
class OrderAssignedTemplate(BaseNotificationTemplate):
    """Template for writer assignment."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order assigned")
        pref = _preheader(ctx, "You have a new assignment.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("order.on_hold")
class OrderOnHoldTemplate(BaseNotificationTemplate):
    """Template for order placed on hold."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order on hold")
        pref = _preheader(ctx, "The order is temporarily on hold.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("order.off_hold")
class OrderOffHoldTemplate(BaseNotificationTemplate):
    """Template for order taken off hold."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order off hold")
        pref = _preheader(ctx, "The order has been taken off hold.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)

@register_template("order.created")
class OrderCreatedTemplate(BaseNotificationTemplate):
    """Template for new order creation."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "New order created")
        pref = _preheader(ctx, "A new order has been placed.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)
    

@register_template("order.submitted")
class OrderSubmittedTemplate(BaseNotificationTemplate):
    """Template for order submission."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order submitted")
        pref = _preheader(ctx, "The order has been submitted for review.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)
    
@register_template("order.updated")
class OrderUpdatedTemplate(BaseNotificationTemplate):
    """Template for order update."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order updated")
        pref = _preheader(ctx, "The order details have been updated.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)



@register_template("order.restored")
class OrderRestoredTemplate(BaseNotificationTemplate):
    """Template for order restored from hold."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order restored")
        pref = _preheader(ctx, "The order has been restored from hold.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("order.revision_requested")
class OrderRevisionRequestedTemplate(BaseNotificationTemplate):
    """Template for client requesting a revision."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Revision requested")
        pref = _preheader(ctx, "Changes were requested.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("order.revision_completed")
class OrderRevisionCompletedTemplate(BaseNotificationTemplate):
    """Template for revision completed."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Revision completed")
        pref = _preheader(ctx, "Revised files are ready.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("order.completed")
class OrderCompletedTemplate(BaseNotificationTemplate):
    """Template for order completion."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order completed")
        pref = _preheader(ctx, "This order is complete.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("order.cancelled")
class OrderCancelledTemplate(BaseNotificationTemplate):
    """Template for order cancellation."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order cancelled")
        pref = _preheader(ctx, "The order has been cancelled.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("order.refunded")
class OrderRefundedTemplate(BaseNotificationTemplate):
    """Template for order refund."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order refunded")
        pref = _preheader(ctx, "A refund has been issued.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("order.disputed")
class OrderDisputedTemplate(BaseNotificationTemplate):
    """Template for order dispute."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order disputed")
        pref = _preheader(ctx, "The order is under dispute.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)
    

@register_template("order.dispute_resolved")
class OrderDisputeResolvedTemplate(BaseNotificationTemplate):
    """Template for order dispute resolution."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order dispute resolved")
        pref = _preheader(ctx, "The dispute has been resolved.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("order.expiring_soon")
class OrderExpiringSoonTemplate(BaseNotificationTemplate):
    """Template for order nearing deadline."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order expiring soon")
        pref = _preheader(ctx, "The order deadline is approaching.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)
    

@register_template("order.late")
class OrderLateTemplate(BaseNotificationTemplate):
    """Template for overdue order."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order late")
        pref = _preheader(ctx, "The order is past its deadline.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)
    

@register_template("order.cancel_request")
class OrderCancelRequestTemplate(BaseNotificationTemplate):
    """Template for order cancellation request."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order cancellation requested")
        pref = _preheader(ctx, "A cancellation has been requested.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)
    

@register_template("order.cancel_request_approved")
class OrderCancelRequestApprovedTemplate(BaseNotificationTemplate):
    """Template for approved cancellation request."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order cancellation approved")
        pref = _preheader(ctx, "The cancellation request has been approved.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)
    

@register_template("order.cancel_request_denied")
class OrderCancelRequestDeniedTemplate(BaseNotificationTemplate):
    """Template for denied cancellation request."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order cancellation denied")
        pref = _preheader(ctx, "The cancellation request has been denied.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)
    

@register_template("order.revision_in_progress")
class OrderRevisionInProgressTemplate(BaseNotificationTemplate):
    """Template for revision in progress."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Revision in progress")
        pref = _preheader(ctx, "Work on the revision has started.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)

@register_template("order.revised")
class OrderRevisedTemplate(BaseNotificationTemplate):
    """Template for revision completed."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order revised")
        pref = _preheader(ctx, "The revision has been completed.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)
    

@register_template("order.revision_cancelled")
class OrderRevisionCancelledTemplate(BaseNotificationTemplate):
    """Template for revision cancelled."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order revision cancelled")
        pref = _preheader(ctx, "The revision has been cancelled.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)

@register_template("order.reopen_request")
class OrderReopenRequestTemplate(BaseNotificationTemplate):
    """Template for order reopen request."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order reopen requested")
        pref = _preheader(ctx, "A request to reopen the order has been made.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)
    
@register_template("order.reopen_request_approved")
class OrderReopenRequestApprovedTemplate(BaseNotificationTemplate):
    """Template for approved reopen request."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order reopen approved")
        pref = _preheader(ctx, "The reopen request has been approved.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)
    
@register_template("order.reopen_request_denied")
class OrderReopenRequestDeniedTemplate(BaseNotificationTemplate):
    """Template for denied reopen request."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order reopen denied")
        pref = _preheader(ctx, "The reopen request has been denied.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)
    

@register_template("order.returned_to_progress")
class OrderReturnedToProgressTemplate(BaseNotificationTemplate):
    """Template for returning order to in-progress."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order returned to progress")
        pref = _preheader(ctx, "The order has been moved back to in-progress.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)

@register_template("order.reassigned")
class OrderReassignedTemplate(BaseNotificationTemplate):
    """Template for writer reassignment."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order reassigned")
        pref = _preheader(ctx, "The order has been reassigned to a new writer.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("order.unassigned")
class OrderUnassignedTemplate(BaseNotificationTemplate):
    """Template for writer unassignment."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Writer unassigned")
        pref = _preheader(ctx, "The writer was removed from the order.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("order.assignment_accepted")
class OrderAssignmentAcceptedTemplate(BaseNotificationTemplate):
    """Template for assignment accepted by writer."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Assignment accepted")
        pref = _preheader(ctx, "A writer accepted the assignment.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("order.assignment_rejected")
class OrderAssignmentRejectedTemplate(BaseNotificationTemplate):
    """Template for assignment rejected by writer."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Assignment rejected")
        pref = _preheader(ctx, "A writer rejected the assignment.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("order.preferred_writer_accepted")
class PreferredWriterAcceptedTemplate(BaseNotificationTemplate):
    """Template for preferred writer acceptance."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Preferred writer accepted")
        pref = _preheader(ctx, "Your preferred writer accepted the order.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("order.preferred_writer_rejected")
class PreferredWriterRejectedTemplate(BaseNotificationTemplate):
    """Template for preferred writer rejection."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Preferred writer rejected")
        pref = _preheader(ctx, "Your preferred writer declined the order.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("order.fined")
class OrderFinedTemplate(BaseNotificationTemplate):
    """Template for order fine applied."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Fine applied")
        pref = _preheader(ctx, "A fine was applied for this order.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)
    
@register_template("order.archived")
class OrderArchivedTemplate(BaseNotificationTemplate):
    """Template for order archival."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order archived")
        pref = _preheader(ctx, "The order has been archived.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)
    
@register_template("order.unarchived")
class OrderUnarchivedTemplate(BaseNotificationTemplate):
    """Template for order unarchival."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order unarchived")
        pref = _preheader(ctx, "The order has been unarchived.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)
    

@register_template("order.deleted")
class OrderDeletedTemplate(BaseNotificationTemplate):
    """Template for order deletion."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order deleted")
        pref = _preheader(ctx, "The order has been deleted.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)

@register_template("order.file_uploaded")
class OrderFileUploadedTemplate(BaseNotificationTemplate):
    """Template for file upload."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "File uploaded")
        pref = _preheader(ctx, "A new file has been uploaded to the order.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)

@register_template("order.file_deleted")
class OrderFileDeletedTemplate(BaseNotificationTemplate):
    """Template for file deletion."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "File deleted")
        pref = _preheader(ctx, "A file has been deleted from the order.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)
    
@register_template("order.approved")
class OrderApprovedTemplate(BaseNotificationTemplate):
    """Template for order approval."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order approved!")
        pref = _preheader(ctx, "Your order has been approved.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("order.rating_submitted")
class OrderRatingSubmittedTemplate(BaseNotificationTemplate):
    """Template for client rating submission."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Rating submitted")
        pref = _preheader(ctx, "The client has submitted a rating.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)
    

@register_template("order.reminder")
class OrderReminderTemplate(BaseNotificationTemplate):
    """Template for order reminder."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order reminder")
        pref = _preheader(ctx, "This is a reminder about your order.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)
    

@register_template("order.reviewed")
class OrderReviewedTemplate(BaseNotificationTemplate):
    """Template for order review."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order reviewed")
        pref = _preheader(ctx, "The order has been reviewed.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)
    
@register_template("order.preferred_writer_assigned")
class OrderPreferredWriterTemplate(BaseNotificationTemplate):
    """Template for preferred-writer assignment."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Preferred writer assigned")
        pref = _preheader(ctx, "Assigned to your preferred writer.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("order.in_progress")
class OrderInProgressTemplate(BaseNotificationTemplate):
    """Template for in-progress state."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order in progress")
        pref = _preheader(ctx, "Work has started on your order.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("order.under_editing")
class OrderUnderEditingTemplate(BaseNotificationTemplate):
    """Template for under-editing state."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order under editing")
        pref = _preheader(ctx, "The order is being edited.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("order.available")
class OrderAvailableTemplate(BaseNotificationTemplate):
    """Template for availability in the writer pool."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order available")
        pref = _preheader(ctx, "This order is available for assignment.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("order.paid")
class OrderPaidTemplate(BaseNotificationTemplate):
    """Template for payment confirmation."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Payment received")
        pref = _preheader(ctx, "Payment has been confirmed.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("order.payment_failed")
class OrderPaymentFailedTemplate(BaseNotificationTemplate):
    """Template for failed payment."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Payment failed")
        pref = _preheader(ctx, "A payment attempt did not go through.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)

@register_template("order.cancellation_requested")
class OrderCancellationRequestedTemplate(BaseNotificationTemplate):
    """Template for order cancellation request."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order cancellation requested")
        pref = _preheader(ctx, "A cancellation has been requested.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("order.closed")
class OrderClosedTemplate(BaseNotificationTemplate):
    """Template for order closure."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order closed")
        pref = _preheader(ctx, "The order has been closed.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)
    

@register_template("order.expired")
class OrderExpiredTemplate(BaseNotificationTemplate):
    """Template for order expiration."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order expired")
        pref = _preheader(ctx, "The order has expired.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)


@register_template("order.rated")
class OrderRatedTemplate(BaseNotificationTemplate):
    """Template for order rating."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order rated")
        pref = _preheader(ctx, "The order has been rated.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)
    
@register_template("order.returned")
class OrderReturnedTemplate(BaseNotificationTemplate):
    """Template for order returned to writer."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order returned to writer")
        pref = _preheader(ctx, "The order has been returned to the writer.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)
    

@register_template("order.unpaid")
class OrderUnpaidTemplate(BaseNotificationTemplate):
    """Template for unpaid order."""

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        title = _title(ctx, "Order unpaid")
        pref = _preheader(ctx, "The order is marked as unpaid.")
        cta_text, cta_url = _cta(ctx)
        body = f"{pref} Order{_order_num(ctx)}."
        return title, body, _html(title, body, cta_text, cta_url)



# Optional: file-based email templates for channels you want to override.
# These names are looked up by your renderer if you support file templates.
register_template_name(
    event_key="order.paid",
    channel="email",
    template_name="notifications/emails/order_paid.html",
)

register_template_name(
    event_key="order.restored",
    channel="email",
    template_name="notifications/emails/order_restored.html",
)
