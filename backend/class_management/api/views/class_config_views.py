from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from class_management.api.serializers.class_config_serializers import (
    ClassServiceConfigSerializer,
)
from class_management.models import ClassServiceConfig
from websites.models.websites import Website


DEFAULT_DURATION_OPTIONS = [
    {"key": "4_weeks", "label": "4 weeks", "weeks": 4},
    {"key": "8_weeks", "label": "8 weeks", "weeks": 8},
    {"key": "12_weeks", "label": "12 weeks", "weeks": 12},
    {"key": "semester", "label": "Full semester", "weeks": 16},
]

DEFAULT_WORKLOAD_OPTIONS = [
    {
        "key": "light",
        "label": "Light",
        "complexity": "low",
        "description": "Routine assignments and discussion posts.",
        "price_hint": "Lower effort",
    },
    {
        "key": "standard",
        "label": "Standard",
        "complexity": "medium",
        "description": "Standard mix of weekly deliverables.",
        "price_hint": "Typical effort",
    },
    {
        "key": "heavy",
        "label": "Heavy",
        "complexity": "high",
        "description": "High-volume or technical coursework.",
        "price_hint": "Higher effort",
    },
]

DEFAULT_TASK_OPTIONS = [
    {"key": "assignments", "label": "Assignments"},
    {"key": "discussions", "label": "Discussion posts"},
    {"key": "quizzes", "label": "Quizzes"},
    {"key": "exams", "label": "Exams"},
    {"key": "papers", "label": "Papers / reports"},
    {"key": "projects", "label": "Projects"},
    {"key": "labs", "label": "Labs / practical work"},
]

DEFAULT_REQUIRED_FIELDS = [
    "title",
    "subject",
    "academic_level",
    "starts_on",
    "ends_on",
]

DEFAULT_CLASS_CONFIGS = [
    {
        "name": "Full class management",
        "slug": "full-class-management",
        "description": (
            "Ongoing support for a complete online class, including weekly "
            "deliverables, monitoring, and coordination."
        ),
        "service_type": "full_class",
        "display_order": 10,
        "requires_portal_access": True,
    },
    {
        "name": "Weekly class support",
        "slug": "weekly-class-support",
        "description": (
            "Recurring weekly help for selected coursework and class tasks."
        ),
        "service_type": "weekly_support",
        "display_order": 20,
        "requires_portal_access": True,
    },
    {
        "name": "Exam and quiz support",
        "slug": "exam-quiz-support",
        "description": (
            "Focused support for exams, quizzes, and assessment windows."
        ),
        "service_type": "exam_quiz",
        "display_order": 30,
        "requires_portal_access": True,
    },
    {
        "name": "Assignments only",
        "slug": "assignments-only",
        "description": "Support limited to assignments, reports, and projects.",
        "service_type": "assignments_only",
        "display_order": 40,
        "requires_portal_access": False,
    },
]


class ClassServiceConfigListView(APIView):
    """
    List class service configs for the resolved tenant website.

    Admins need inactive rows for configuration management. Non-admin callers
    only receive active configs for client-facing class order flows.
    """

    permission_classes = [IsAuthenticated]

    @staticmethod
    def _can_manage(user) -> bool:
        role = getattr(user, "role", None)
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or role in {"superadmin", "admin"})
        )

    def _website(self, request):
        requested_website_id = request.query_params.get("website_id")
        role = getattr(request.user, "role", None)
        if requested_website_id and (
            request.user.is_superuser or role == "superadmin"
        ):
            website = Website.objects.filter(pk=requested_website_id).first()
            if website is None:
                raise NotFound("Website not found.")
            return website

        return getattr(request, "website", None) or getattr(
            request.user,
            "website",
            None,
        )

    def get(self, request):
        website = self._website(request)
        queryset = ClassServiceConfig.objects.none()
        if website is not None:
            queryset = ClassServiceConfig.objects.filter(
                website=website,
            ).order_by("display_order", "name")
            if not self._can_manage(request.user):
                queryset = queryset.filter(is_active=True)

        serializer = ClassServiceConfigSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not self._can_manage(request.user):
            return Response({"detail": "Admin only."}, status=status.HTTP_403_FORBIDDEN)

        website = self._website(request)
        serializer = ClassServiceConfigSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        config = serializer.save(
            website=website,
            created_by=request.user,
        )
        return Response(
            ClassServiceConfigSerializer(config).data,
            status=status.HTTP_201_CREATED,
        )


class ClassServiceConfigSeedDefaultsView(ClassServiceConfigListView):
    """
    Create or refresh the tenant's default class-service presets.
    """

    def post(self, request):
        if not self._can_manage(request.user):
            return Response({"detail": "Admin only."}, status=status.HTTP_403_FORBIDDEN)

        website = self._website(request)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created = 0
        updated = 0
        with transaction.atomic():
            for row in DEFAULT_CLASS_CONFIGS:
                config, was_created = ClassServiceConfig.objects.update_or_create(
                    website=website,
                    slug=row["slug"],
                    defaults={
                        "name": row["name"],
                        "description": row["description"],
                        "service_type": row["service_type"],
                        "pricing_mode": ClassServiceConfig.PRICING_MODE_QUOTE,
                        "base_price": Decimal("0.00"),
                        "currency": "USD",
                        "duration_options": DEFAULT_DURATION_OPTIONS,
                        "workload_options": DEFAULT_WORKLOAD_OPTIONS,
                        "task_options": DEFAULT_TASK_OPTIONS,
                        "required_fields": DEFAULT_REQUIRED_FIELDS,
                        "requires_portal_access": row["requires_portal_access"],
                        "allow_installments": True,
                        "require_deposit_before_start": True,
                        "deposit_percentage": Decimal("50.00"),
                        "quote_expiry_hours": 72,
                        "is_active": True,
                        "display_order": row["display_order"],
                    },
                )
                if was_created:
                    config.created_by = request.user
                    config.save(update_fields=["created_by", "updated_at"])
                    created += 1
                else:
                    updated += 1

        return Response({"created": created, "updated": updated})


class ClassServiceConfigDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _can_manage(user) -> bool:
        role = getattr(user, "role", None)
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or role in {"superadmin", "admin"})
        )

    def _get_config(self, request, pk: int):
        website = getattr(request, "website", None) or getattr(
            request.user,
            "website",
            None,
        )
        qs = ClassServiceConfig.objects.filter(pk=pk)
        if not (request.user.is_superuser or getattr(request.user, "role", None) == "superadmin"):
            qs = qs.filter(website=website)
        return qs.first()

    def get(self, request, pk: int):
        config = self._get_config(request, pk)
        if config is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ClassServiceConfigSerializer(config).data)

    def patch(self, request, pk: int):
        if not self._can_manage(request.user):
            return Response({"detail": "Admin only."}, status=status.HTTP_403_FORBIDDEN)

        config = self._get_config(request, pk)
        if config is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ClassServiceConfigSerializer(
            config,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
