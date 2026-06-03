from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from decimal import Decimal
from typing import Any
from urllib.parse import urlparse

from django.db.models import Q
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from admin_management.models import OperationsCommandItemEvent, OperationsCommandItemState
from class_management.constants import ClassOrderStatus, ClassPaymentStatus
from class_management.models import ClassOrder
from cms_intelligence.models import FreshnessAlert
from orders.enums import OrderPaymentStatus, OrderStatus
from orders.models.orders import Order
from special_orders.constants import SpecialOrderPriority, SpecialOrderStatus
from special_orders.models import SpecialOrder
from tickets.models import Ticket
from websites.models.websites import Website
from writer_vetting.models import AttemptStatus, WriterTestAttempt


from orders.services.order_available_actions_service import OrderAvailableActionsService

STAFF_ROLES = {"superadmin", "admin", "editor", "support"}


class CanViewOperationsCommandCenter(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return bool(
            getattr(request.user, "is_staff", False)
            or getattr(request.user, "role", None) in STAFF_ROLES
        )


@dataclass
class CommandItem:
    score: int
    id: str
    domain: str
    priority: str
    title: str
    description: str
    website: dict[str, Any] | None
    entity: dict[str, Any]
    action_label: str
    action_url: str
    created_at: str | None = None
    due_at: str | None = None
    meta: list[dict[str, str]] = field(default_factory=list)
    state: dict[str, Any] | None = None
    available_actions: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "domain": self.domain,
            "priority": self.priority,
            "score": self.score,
            "title": self.title,
            "description": self.description,
            "website": self.website,
            "entity": self.entity,
            "action_label": self.action_label,
            "action_url": self.action_url,
            "created_at": self.created_at,
            "due_at": self.due_at,
            "meta": self.meta,
            "state": self.state,
            "available_actions": self.available_actions,
        }


def _order_actions(order: Any, user: Any) -> list[str]:
    if user is None:
        return []
    try:
        return OrderAvailableActionsService.build_actions(
            order=order,
            user=user,
            lifecycle=None,
        )
    except Exception:
        return []


def _website_dict(website: Website | None) -> dict[str, Any] | None:
    if website is None:
        return None
    return {
        "id": website.pk,
        "name": website.name,
        "domain": website.domain,
    }


def _iso(value) -> str | None:
    return value.isoformat() if value else None


def _money(value: Decimal | int | float | None, currency: str = "USD") -> str:
    amount = Decimal(str(value or "0"))
    return f"{currency} {amount.quantize(Decimal('0.01'))}"


def _display(value: str | None) -> str:
    return (value or "unknown").replace("_", " ").title()


def _priority(score: int) -> str:
    if score >= 90:
        return "critical"
    if score >= 75:
        return "high"
    if score >= 50:
        return "medium"
    return "low"


def _domain_from_website(website: Website | None) -> str | None:
    if not website:
        return None
    raw = website.domain or ""
    parsed = urlparse(raw if "://" in raw else f"https://{raw}")
    return (parsed.hostname or raw).lower().removeprefix("www.")


class OperationsCommandCenterViewSet(ViewSet):
    permission_classes = [CanViewOperationsCommandCenter]

    def list(self, request):
        scope_website = self._scope_website(request)
        items: list[CommandItem] = []

        items.extend(self._order_deadline_items(scope_website, request.user))
        items.extend(self._order_payment_items(scope_website, request.user))
        items.extend(self._writer_review_items(scope_website))
        items.extend(self._class_order_items(scope_website))
        items.extend(self._special_order_items(scope_website))
        items.extend(self._ticket_items(scope_website))
        items.extend(self._cms_items(scope_website))

        items = self._apply_item_states(items)
        items = sorted(items, key=lambda item: (-item.score, item.created_at or ""))[:80]
        summary = self._summary(items)

        return Response(
            {
                "generated_at": timezone.now().isoformat(),
                "scope": {
                    "website_id": scope_website.pk if scope_website else None,
                    "website_name": scope_website.name if scope_website else None,
                    "is_cross_tenant": scope_website is None
                    and getattr(request.user, "role", None) == "superadmin",
                },
                "summary": summary,
                "items": [item.as_dict() for item in items],
            }
        )

    @action(detail=False, methods=["post"], url_path="item-action")
    def item_action(self, request):
        item_id = str(request.data.get("item_id") or "").strip()
        action_name = str(request.data.get("action") or "").strip()
        if not item_id:
            return Response({"detail": "item_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        if action_name not in {"acknowledge", "snooze", "resolve", "reopen", "claim", "release"}:
            return Response({"detail": "Unsupported action."}, status=status.HTTP_400_BAD_REQUEST)

        website = self._state_website_for_request(request)
        if website is False:
            return Response(
                {"detail": "Cannot act on an item outside your website scope."},
                status=status.HTTP_403_FORBIDDEN,
            )

        entity = request.data.get("entity") or {}
        now = timezone.now()
        state_obj, _ = OperationsCommandItemState.objects.get_or_create(
            item_id=item_id,
            defaults={
                "domain": str(request.data.get("domain") or ""),
                "entity_type": str(entity.get("type") or ""),
                "entity_id": entity.get("id") if entity.get("id") else None,
                "entity_label": str(entity.get("label") or ""),
                "website": website,
            },
        )

        state_obj.domain = str(request.data.get("domain") or state_obj.domain or "")
        state_obj.entity_type = str(entity.get("type") or state_obj.entity_type or "")
        state_obj.entity_id = entity.get("id") if entity.get("id") else state_obj.entity_id
        state_obj.entity_label = str(entity.get("label") or state_obj.entity_label or "")
        state_obj.website = website or state_obj.website
        state_obj.updated_by = request.user
        state_obj.note = str(request.data.get("note") or "").strip()
        from_status = state_obj.status

        if action_name == "acknowledge":
            state_obj.status = OperationsCommandItemState.Status.ACKNOWLEDGED
            state_obj.acknowledged_by = request.user
            state_obj.acknowledged_at = now
            state_obj.snoozed_until = None
        elif action_name == "claim":
            state_obj.assigned_to = request.user
            state_obj.assigned_at = now
            if state_obj.status == OperationsCommandItemState.Status.ACTIVE:
                state_obj.status = OperationsCommandItemState.Status.ACKNOWLEDGED
                state_obj.acknowledged_by = request.user
                state_obj.acknowledged_at = now
        elif action_name == "release":
            state_obj.assigned_to = None
            state_obj.assigned_at = None
        elif action_name == "snooze":
            state_obj.status = OperationsCommandItemState.Status.SNOOZED
            state_obj.acknowledged_by = request.user
            state_obj.acknowledged_at = state_obj.acknowledged_at or now
            state_obj.snoozed_until = self._parse_snooze_until(request)
        elif action_name == "resolve":
            state_obj.status = OperationsCommandItemState.Status.RESOLVED
            state_obj.resolved_by = request.user
            state_obj.resolved_at = now
            state_obj.snoozed_until = None
        elif action_name == "reopen":
            state_obj.status = OperationsCommandItemState.Status.ACTIVE
            state_obj.resolved_by = None
            state_obj.resolved_at = None
            state_obj.snoozed_until = None

        state_obj.save()
        self._record_event(
            state_obj,
            action=action_name,
            actor=request.user,
            note=state_obj.note,
            from_status=from_status,
        )
        return Response({"state": self._state_dict(state_obj)})

    @action(detail=False, methods=["get"], url_path="item-history")
    def item_history(self, request):
        item_id = str(request.query_params.get("item_id") or "").strip()
        if not item_id:
            return Response({"detail": "item_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        state = OperationsCommandItemState.objects.filter(item_id=item_id).select_related("website").first()
        if state is None:
            return Response({"item_id": item_id, "events": []})
        scoped = self._scope_website(request)
        if getattr(request.user, "role", None) != "superadmin" and scoped and state.website_id != scoped.pk:
            return Response({"detail": "Cannot view history outside your website scope."}, status=status.HTTP_403_FORBIDDEN)

        qs = (
            OperationsCommandItemEvent.objects.filter(state=state)
            .select_related("actor", "state")
            .order_by("-created_at")[:30]
        )
        return Response(
            {
                "item_id": item_id,
                "events": [
                    {
                        "id": event.pk,
                        "action": event.action,
                        "note": event.note,
                        "actor": getattr(event.actor, "username", None),
                        "actor_id": getattr(event.actor, "id", None),
                        "from_status": event.from_status,
                        "to_status": event.to_status,
                        "metadata": event.metadata,
                        "created_at": _iso(event.created_at),
                    }
                    for event in qs
                ],
            }
        )

    def _scope_website(self, request) -> Website | None:
        role = getattr(request.user, "role", None)
        website_id = request.query_params.get("website_id")
        if role == "superadmin":
            if website_id:
                return Website.objects.filter(pk=website_id).first()
            return None

        request_website = getattr(request, "website", None)
        if request_website:
            return request_website
        return getattr(request.user, "website", None)

    def _website_filter(self, website: Website | None) -> Q:
        return Q() if website is None else Q(website=website)

    def _state_website_for_request(self, request) -> Website | None | bool:
        website_id = request.data.get("website_id")
        role = getattr(request.user, "role", None)
        if role == "superadmin":
            if website_id in ("", None):
                return None
            return Website.objects.filter(pk=website_id).first()

        scoped = self._scope_website(request)
        if website_id and scoped and int(website_id) != scoped.pk:
            return False
        return scoped

    def _parse_snooze_until(self, request):
        raw_until = request.data.get("snoozed_until")
        if raw_until:
            parsed = parse_datetime(str(raw_until))
            if parsed:
                return parsed if timezone.is_aware(parsed) else timezone.make_aware(parsed)
        hours = request.data.get("snooze_hours") or 24
        try:
            hours = max(1, min(int(hours), 24 * 30))
        except (TypeError, ValueError):
            hours = 24
        return timezone.now() + timedelta(hours=hours)

    def _apply_item_states(self, items: list[CommandItem]) -> list[CommandItem]:
        if not items:
            return []
        now = timezone.now()
        states = {
            item.item_id: item
            for item in OperationsCommandItemState.objects.filter(
                item_id__in=[item.id for item in items],
            ).select_related("assigned_to", "updated_by", "acknowledged_by", "resolved_by")
        }
        visible: list[CommandItem] = []
        for item in items:
            state_obj = states.get(item.id)
            if state_obj:
                if state_obj.status == OperationsCommandItemState.Status.RESOLVED:
                    continue
                if (
                    state_obj.status == OperationsCommandItemState.Status.SNOOZED
                    and state_obj.snoozed_until
                    and state_obj.snoozed_until > now
                ):
                    continue
                if (
                    state_obj.status == OperationsCommandItemState.Status.SNOOZED
                    and state_obj.snoozed_until
                    and state_obj.snoozed_until <= now
                ):
                    state_obj.status = OperationsCommandItemState.Status.ACKNOWLEDGED
                    state_obj.snoozed_until = None
                    state_obj.save(update_fields=["status", "snoozed_until", "updated_at"])
                item.state = self._state_dict(state_obj)
            else:
                item.state = {
                    "status": OperationsCommandItemState.Status.ACTIVE,
                    "note": "",
                    "snoozed_until": None,
                    "assigned_to": None,
                    "assigned_to_id": None,
                    "assigned_at": None,
                    "updated_by": None,
                    "updated_at": None,
                    "acknowledged_at": None,
                    "resolved_at": None,
                }
            visible.append(item)
        return visible

    def _state_dict(self, item: OperationsCommandItemState) -> dict[str, Any]:
        return {
            "status": item.status,
            "note": item.note,
            "snoozed_until": _iso(item.snoozed_until),
            "assigned_to": getattr(item.assigned_to, "username", None),
            "assigned_to_id": getattr(item.assigned_to, "id", None),
            "assigned_at": _iso(item.assigned_at),
            "updated_by": getattr(item.updated_by, "username", None),
            "updated_at": _iso(item.updated_at),
            "acknowledged_at": _iso(item.acknowledged_at),
            "resolved_at": _iso(item.resolved_at),
        }

    def _record_event(
        self,
        state: OperationsCommandItemState,
        *,
        action: str,
        actor,
        note: str,
        from_status: str,
    ) -> None:
        OperationsCommandItemEvent.objects.create(
            state=state,
            action=action,
            note=note,
            actor=actor,
            from_status=from_status,
            to_status=state.status,
            metadata={
                "assigned_to_id": getattr(state.assigned_to, "id", None),
                "assigned_to": getattr(state.assigned_to, "username", None),
                "snoozed_until": _iso(state.snoozed_until),
            },
        )

    def _order_deadline_items(self, website: Website | None, user=None) -> list[CommandItem]:
        now = timezone.now()
        soon = now + timedelta(hours=24)
        closed = [
            OrderStatus.COMPLETED,
            OrderStatus.CANCELLED,
            OrderStatus.REFUNDED,
            OrderStatus.ARCHIVED,
        ]
        orders = (
            Order.objects.filter(self._website_filter(website))
            .exclude(status__in=closed)
            .filter(Q(client_deadline__lte=soon) | Q(writer_deadline__lte=soon))
            .select_related("website", "client")
            .order_by("client_deadline")[:30]
        )
        items: list[CommandItem] = []
        for order in orders:
            due = order.writer_deadline or order.client_deadline
            overdue = bool(due and due < now)
            hours_left = ((due - now).total_seconds() / 3600) if due else 24
            score = 96 if overdue else 88 if hours_left <= 6 else 72
            label = "overdue" if overdue else "due soon"
            items.append(
                CommandItem(
                    id=f"order-deadline-{order.pk}",
                    domain="orders",
                    priority=_priority(score),
                    score=score,
                    title=f"Order {label}",
                    description=f"{order.topic} needs operational attention before the deadline.",
                    website=_website_dict(order.website),
                    entity={"type": "order", "id": order.pk, "label": order.topic},
                    action_label="Open order",
                    action_url=f"/admin/orders/{order.pk}",
                    created_at=_iso(order.created_at),
                    due_at=_iso(due),
                    meta=[
                        {"label": "Status", "value": _display(order.status)},
                        {"label": "Client deadline", "value": _iso(order.client_deadline) or "Not set"},
                    ],
                    available_actions=_order_actions(order, user),
                )
            )

        awaiting_ack = (
            Order.objects.filter(self._website_filter(website))
            .filter(
                status__in=[
                    OrderStatus.IN_PROGRESS,
                    OrderStatus.READY_FOR_STAFFING,
                    OrderStatus.PAID,
                ],
                last_writer_acknowledged_at__isnull=True,
            )
            .select_related("website")
            .order_by("writer_deadline", "created_at")[:20]
        )
        for order in awaiting_ack:
            items.append(
                CommandItem(
                    id=f"order-writer-ack-{order.pk}",
                    domain="writers",
                    priority="medium",
                    score=58,
                    title="Writer acknowledgement missing",
                    description=f"{order.topic} has no recorded writer acknowledgement yet.",
                    website=_website_dict(order.website),
                    entity={"type": "order", "id": order.pk, "label": order.topic},
                    action_label="Review staffing",
                    action_url=f"/admin/orders/{order.pk}",
                    created_at=_iso(order.created_at),
                    due_at=_iso(order.writer_deadline),
                    meta=[{"label": "Status", "value": _display(order.status)}],
                    available_actions=_order_actions(order, user),
                )
            )
        return items

    def _order_payment_items(self, website: Website | None, user=None) -> list[CommandItem]:
        orders = (
            Order.objects.filter(self._website_filter(website), total_price__gt=0)
            .exclude(payment_status__in=[OrderPaymentStatus.FULLY_PAID, OrderPaymentStatus.REFUNDED])
            .select_related("website")
            .order_by("-created_at")[:25]
        )
        items: list[CommandItem] = []
        for order in orders:
            balance = order.remaining_balance
            score = 82 if balance > 0 and order.status not in [OrderStatus.CREATED, OrderStatus.UNPAID] else 62
            items.append(
                CommandItem(
                    id=f"order-payment-{order.pk}",
                    domain="payments",
                    priority=_priority(score),
                    score=score,
                    title="Payment needs attention",
                    description=f"{order.topic} has an outstanding balance of {_money(balance, order.currency)}.",
                    website=_website_dict(order.website),
                    entity={"type": "order", "id": order.pk, "label": order.topic},
                    action_label="Open payment",
                    action_url=f"/admin/orders/{order.pk}",
                    created_at=_iso(order.created_at),
                    due_at=_iso(order.client_deadline),
                    meta=[
                        {"label": "Paid", "value": _money(order.amount_paid, order.currency)},
                        {"label": "Total", "value": _money(order.total_price, order.currency)},
                    ],
                    available_actions=_order_actions(order, user),
                )
            )
        return items

    def _writer_review_items(self, website: Website | None) -> list[CommandItem]:
        qs = (
            WriterTestAttempt.objects.filter(status=AttemptStatus.PENDING_REVIEW)
            .select_related("quiz", "quiz__website", "writer", "writer__user")
            .order_by("submitted_at", "started_at")[:25]
        )
        if website is not None:
            qs = qs.filter(quiz__website=website)
        items = []
        for attempt in qs:
            submitted = attempt.submitted_at or attempt.started_at
            stale = bool(submitted and submitted <= timezone.now() - timedelta(days=2))
            score = 76 if stale else 54
            writer_name = str(attempt.writer)
            items.append(
                CommandItem(
                    id=f"writer-vetting-{attempt.pk}",
                    domain="writers",
                    priority=_priority(score),
                    score=score,
                    title="Writer essay needs review",
                    description=f"{writer_name} submitted {attempt.quiz.title} and is waiting for staff grading.",
                    website=_website_dict(attempt.quiz.website),
                    entity={"type": "writer_vetting_attempt", "id": attempt.pk, "label": writer_name},
                    action_label="Review essay",
                    action_url="/admin/writer-vetting",
                    created_at=_iso(submitted),
                    meta=[{"label": "Quiz", "value": attempt.quiz.title}],
                )
            )
        return items

    def _class_order_items(self, website: Website | None) -> list[CommandItem]:
        qs = (
            ClassOrder.objects.filter(self._website_filter(website), is_active=True)
            .exclude(status__in=[ClassOrderStatus.COMPLETED, ClassOrderStatus.CANCELLED, ClassOrderStatus.ARCHIVED])
            .filter(
                Q(is_work_paused=True)
                | Q(payment_status__in=[ClassPaymentStatus.UNPAID, ClassPaymentStatus.PARTIALLY_PAID, ClassPaymentStatus.OVERDUE])
                | Q(ends_on__lte=timezone.now().date() + timedelta(days=7))
            )
            .select_related("website", "client")
            .order_by("-is_work_paused", "ends_on", "-created_at")[:25]
        )
        items = []
        for class_order in qs:
            if class_order.is_work_paused:
                score = 84
                title = "Class work is paused"
            elif class_order.payment_status == ClassPaymentStatus.OVERDUE:
                score = 80
                title = "Class payment overdue"
            else:
                score = 56
                title = "Class order needs review"
            items.append(
                CommandItem(
                    id=f"class-order-{class_order.pk}",
                    domain="classes",
                    priority=_priority(score),
                    score=score,
                    title=title,
                    description=f"{class_order.title} has an operational condition staff should review.",
                    website=_website_dict(class_order.website),
                    entity={"type": "class_order", "id": class_order.pk, "label": class_order.title},
                    action_label="Open class",
                    action_url=f"/admin/classes/{class_order.pk}",
                    created_at=_iso(class_order.created_at),
                    due_at=class_order.ends_on.isoformat() if class_order.ends_on else None,
                    meta=[
                        {"label": "Status", "value": _display(class_order.status)},
                        {"label": "Payment", "value": _display(class_order.payment_status)},
                    ],
                )
            )
        return items

    def _special_order_items(self, website: Website | None) -> list[CommandItem]:
        stale_cutoff = timezone.now() - timedelta(days=2)
        qs = (
            SpecialOrder.objects.filter(self._website_filter(website))
            .exclude(status__in=[SpecialOrderStatus.COMPLETED, SpecialOrderStatus.CANCELLED, SpecialOrderStatus.REFUNDED])
            .filter(
                Q(priority__in=[SpecialOrderPriority.HIGH, SpecialOrderPriority.URGENT, SpecialOrderPriority.CRITICAL])
                | Q(status__in=[SpecialOrderStatus.INQUIRY, SpecialOrderStatus.QUOTE_PENDING, SpecialOrderStatus.AWAITING_PAYMENT])
                | Q(created_at__lte=stale_cutoff)
            )
            .select_related("website", "client")
            .order_by("-priority", "created_at")[:25]
        )
        score_by_priority = {
            SpecialOrderPriority.CRITICAL: 94,
            SpecialOrderPriority.URGENT: 86,
            SpecialOrderPriority.HIGH: 74,
        }
        items = []
        for special in qs:
            score = score_by_priority.get(special.priority, 60 if special.created_at <= stale_cutoff else 48)
            items.append(
                CommandItem(
                    id=f"special-order-{special.pk}",
                    domain="special_orders",
                    priority=_priority(score),
                    score=score,
                    title="Special order needs attention",
                    description=f"{special.title} is {_display(special.status)} with {_display(special.priority)} priority.",
                    website=_website_dict(special.website),
                    entity={"type": "special_order", "id": special.pk, "label": special.title},
                    action_label="Open special order",
                    action_url=f"/admin/special-orders/{special.pk}",
                    created_at=_iso(special.created_at),
                    meta=[
                        {"label": "Status", "value": _display(special.status)},
                        {"label": "Priority", "value": _display(special.priority)},
                    ],
                )
            )
        return items

    def _ticket_items(self, website: Website | None) -> list[CommandItem]:
        qs = (
            Ticket.objects.filter(self._website_filter(website))
            .exclude(status="closed")
            .filter(Q(priority__in=["high", "critical"]) | Q(is_escalated=True))
            .select_related("website", "created_by", "assigned_to")
            .order_by("-is_escalated", "-priority", "created_at")[:20]
        )
        items = []
        for ticket in qs:
            score = 90 if ticket.priority == "critical" or ticket.is_escalated else 72
            items.append(
                CommandItem(
                    id=f"ticket-{ticket.pk}",
                    domain="support",
                    priority=_priority(score),
                    score=score,
                    title="Support ticket escalated",
                    description=ticket.title,
                    website=_website_dict(ticket.website),
                    entity={"type": "ticket", "id": ticket.pk, "label": ticket.title},
                    action_label="Open support",
                    action_url="/admin/support",
                    created_at=_iso(ticket.created_at),
                    meta=[
                        {"label": "Priority", "value": _display(ticket.priority)},
                        {"label": "Status", "value": _display(ticket.status)},
                    ],
                )
            )
        return items

    def _cms_items(self, website: Website | None) -> list[CommandItem]:
        qs = FreshnessAlert.objects.filter(resolved_at__isnull=True, severity__gte=3).select_related("site")
        if website is not None:
            host = _domain_from_website(website)
            if not host:
                return []
            qs = qs.filter(Q(site__hostname=host) | Q(site__hostname=f"www.{host}"))
        qs = qs.order_by("-severity", "-raised_at")[:20]
        items = []
        for alert in qs:
            score = min(96, 45 + int(alert.severity) * 12)
            items.append(
                CommandItem(
                    id=f"cms-alert-{alert.pk}",
                    domain="cms",
                    priority=_priority(score),
                    score=score,
                    title="Content freshness alert",
                    description=f"{_display(alert.alert_type)} on {getattr(alert.content_object, 'title', 'content page')}.",
                    website=(
                        _website_dict(website)
                        if website
                        else {"id": None, "name": alert.site.hostname, "domain": alert.site.hostname}
                    ),
                    entity={"type": "freshness_alert", "id": alert.pk, "label": _display(alert.alert_type)},
                    action_label="Open content graph",
                    action_url="/admin/content-graph",
                    created_at=_iso(alert.raised_at),
                    meta=[{"label": "Severity", "value": str(alert.severity)}],
                )
            )
        return items

    def _summary(self, items: list[CommandItem]) -> dict[str, int]:
        summary = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "total": len(items),
            "orders_at_risk": 0,
            "payments_need_attention": 0,
            "writer_reviews": 0,
            "cms_alerts": 0,
            "support_escalations": 0,
            "assigned": 0,
            "unassigned": 0,
        }
        for item in items:
            summary[item.priority] += 1
            if item.domain == "orders":
                summary["orders_at_risk"] += 1
            if item.domain == "payments":
                summary["payments_need_attention"] += 1
            if item.domain == "writers":
                summary["writer_reviews"] += 1
            if item.domain == "cms":
                summary["cms_alerts"] += 1
            if item.domain == "support":
                summary["support_escalations"] += 1
            if (item.state or {}).get("assigned_to_id"):
                summary["assigned"] = summary.get("assigned", 0) + 1
            else:
                summary["unassigned"] = summary.get("unassigned", 0) + 1
        return summary
