from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.db.models import QuerySet

from activity.constants import ActivityAudience
from activity.models import ActivityEvent


class ActivityEventSelector:
    """
    Read helpers for activity events.
    """

    @staticmethod
    def for_website(*, website) -> QuerySet[ActivityEvent]:
        """
        Return activity events for a tenant.
        """
        return ActivityEvent.objects.filter(
            website=website,
        )

    @staticmethod
    def for_target(
        *,
        website,
        target,
    ) -> QuerySet[ActivityEvent]:
        """
        Return activity events for a target object.
        """
        return ActivityEvent.objects.filter(
            website=website,
            target_content_type__app_label=target._meta.app_label,
            target_content_type__model=target._meta.model_name,
            target_object_id=str(target.pk),
        )

    @staticmethod
    def visible_to_audience(
        *,
        website,
        audience: str,
    ) -> QuerySet[ActivityEvent]:
        """
        Return events visible to a given audience.
        """
        return ActivityEvent.objects.filter(
            website=website,
            audiences__contains=[audience],
        )

    @staticmethod
    def visible_to_user(
        *,
        website,
        user,
    ) -> QuerySet[ActivityEvent]:
        """
        Return events visible to the given user.
        """
        queryset = ActivityEvent.objects.all()
        if website is not None:
            queryset = queryset.filter(website=website)

        role = getattr(user, "role", "")
        if role in {"admin", "superadmin"} or getattr(user, "is_superuser", False):
            return queryset.select_related(
                "website",
                "actor_content_type",
                "target_content_type",
                "subject_content_type",
            )

        return queryset.filter(
            ActivityEventSelector._visibility_q_for_user(user=user),
        ).distinct().select_related(
            "website",
            "actor_content_type",
            "target_content_type",
            "subject_content_type",
        )

    @staticmethod
    def visible_to_user_global(*, user) -> QuerySet[ActivityEvent]:
        """
        Return globally visible events for roles allowed to cross tenants.
        """
        return ActivityEventSelector.visible_to_user(
            website=None,
            user=user,
        )

    @staticmethod
    def user_can_view(
        *,
        event: ActivityEvent,
        user,
    ) -> bool:
        """
        Return whether a user can view an event.
        """
        role = getattr(user, "role", "")
        if role in {"admin", "superadmin"} or getattr(user, "is_superuser", False):
            return True

        return ActivityEvent.objects.filter(
            pk=event.pk,
        ).filter(
            ActivityEventSelector._visibility_q_for_user(user=user),
        ).exists()

    @staticmethod
    def get_user_audience(*, user) -> str:
        """
        Resolve a user's activity audience.
        """
        if getattr(user, "is_superuser", False):
            return ActivityAudience.SUPERADMIN

        if getattr(user, "is_staff", False):
            return ActivityAudience.STAFF

        role = getattr(user, "role", "")

        if role == ActivityAudience.WRITER:
            return ActivityAudience.WRITER

        return ActivityAudience.CLIENT

    @staticmethod
    def _visibility_q_for_user(*, user) -> Q:
        """
        Build role-aware feed visibility.

        Personal events are always visible to the actor. Order-scoped events
        are visible to clients, writers, support, and editors allowed to work
        on that order, so both sides can see shared order activity such as
        draft uploads and messages.
        """
        role = getattr(user, "role", "")
        own_q = ActivityEventSelector._actor_user_q(user=user)

        if role == "client":
            return own_q | ActivityEventSelector._order_scope_q(
                order_ids=ActivityEventSelector._client_order_ids(user=user),
            )

        if role == "writer":
            return own_q | ActivityEventSelector._order_scope_q(
                order_ids=ActivityEventSelector._writer_order_ids(user=user),
            )

        if role == "support":
            return (
                own_q
                | ActivityEventSelector._actor_roles_q(roles=["client", "writer"])
                | ActivityEventSelector._order_scope_q(
                    order_ids=ActivityEventSelector._support_order_ids(user=user),
                )
            )

        if role == "editor":
            return own_q | ActivityEventSelector._order_scope_q(
                order_ids=ActivityEventSelector._editor_order_ids(user=user),
            )

        audience = ActivityEventSelector.get_user_audience(user=user)
        return own_q | Q(audiences__contains=[audience])

    @staticmethod
    def _actor_user_q(*, user) -> Q:
        return Q(
            actor_content_type=ActivityEventSelector._user_content_type(),
            actor_object_id=str(getattr(user, "pk", "")),
        )

    @staticmethod
    def _actor_roles_q(*, roles: list[str]) -> Q:
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user_ids = User.objects.filter(role__in=roles).values_list("pk", flat=True)
        return Q(
            actor_content_type=ActivityEventSelector._user_content_type(),
            actor_object_id__in=[str(user_id) for user_id in user_ids],
        )

    @staticmethod
    def _order_scope_q(*, order_ids) -> Q:
        ids = [str(order_id) for order_id in order_ids]
        if not ids:
            return Q(pk__in=[])

        order_content_type = ActivityEventSelector._order_content_type()
        return (
            Q(target_content_type=order_content_type, target_object_id__in=ids)
            | Q(subject_content_type=order_content_type, subject_object_id__in=ids)
            | Q(metadata__order_id__in=ids)
            | Q(metadata__order__id__in=ids)
        )

    @staticmethod
    def _client_order_ids(*, user):
        from orders.selectors.order_visibility_selector import OrderVisibilitySelector

        return OrderVisibilitySelector.visible_to_client(
            client=user,
        ).values_list("pk", flat=True)

    @staticmethod
    def _writer_order_ids(*, user):
        from orders.selectors.order_visibility_selector import OrderVisibilitySelector

        return OrderVisibilitySelector.visible_to_writer(
            writer=user,
        ).values_list("pk", flat=True)

    @staticmethod
    def _support_order_ids(*, user):
        from orders.selectors.order_visibility_selector import OrderVisibilitySelector

        return OrderVisibilitySelector.visible_to_staff(
            staff_user=user,
        ).values_list("pk", flat=True)

    @staticmethod
    def _editor_order_ids(*, user):
        try:
            profile = user.editor_profile
        except Exception:
            return []

        try:
            from editor_management.models import EditorTaskAssignment

            return EditorTaskAssignment.objects.filter(
                assigned_editor=profile,
            ).values_list("order_id", flat=True)
        except Exception:
            return []

    @staticmethod
    def _user_content_type():
        from django.contrib.auth import get_user_model

        return ContentType.objects.get_for_model(get_user_model())

    @staticmethod
    def _order_content_type():
        from orders.models.orders.order import Order

        return ContentType.objects.get_for_model(Order)
