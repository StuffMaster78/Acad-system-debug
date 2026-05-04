# class_management/api/views/class_scope_views.py

from __future__ import annotations

from decimal import Decimal
from typing import cast, Any

from django.contrib.auth import get_user_model

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from class_management.api.permissions import ClassScopePermission
from class_management.api.serializers.class_scope_serializers import (
    ClassScopeAssessmentSerializer,
    ClassScopeItemSerializer,
    ClassTaskActionSerializer,
    ClassTaskSerializer,
    CreateClassTaskSerializer,
)
from class_management.models.class_scope import ClassScopeItem, ClassTask
from class_management.selectors import ClassOrderSelector, ClassScopeSelector
from class_management.services.class_scope_service import ClassScopeService
from class_management.api.views.class_base_views import ClassTenantViewMixin


class ClassScopeItemViewSet(ClassTenantViewMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, ClassScopePermission]

    def get_class_order(self):
        return ClassOrderSelector.get_for_website(
            website=self.get_website(),
            class_order_id=self.kwargs["class_order_pk"],
        )

    def list(self, request, *args, **kwargs):
        class_order = self.get_class_order()
        items = ClassScopeSelector.scope_items_for_order(
            class_order=class_order,
        )
        return Response(ClassScopeItemSerializer(items, many=True).data)

    def create(self, request, *args, **kwargs):
        class_order = self.get_class_order()
        serializer = ClassScopeItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        item = ClassScopeService.add_scope_item(
            class_order=class_order,
            item_type=data["item_type"],
            title=data["title"],
            created_by=request.user,
            quantity=data.get("quantity", 1),
            due_at=data.get("due_at"),
            estimated_pages=data.get("estimated_pages"),
            estimated_words=data.get("estimated_words"),
            estimated_hours=data.get("estimated_hours"),
            complexity_level=data.get("complexity_level", "medium"),
            notes=data.get("notes", ""),
        )

        return Response(
            ClassScopeItemSerializer(item).data,
            status=status.HTTP_201_CREATED,
        )


class ClassTaskViewSet(ClassTenantViewMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, ClassScopePermission]

    def get_class_order(self):
        return ClassOrderSelector.get_for_website(
            website=self.get_website(),
            class_order_id=self.kwargs["class_order_pk"],
        )

    def get_task(self) -> ClassTask:
        class_order = self.get_class_order()
        task = ClassTask.objects.get(
            pk=self.kwargs["pk"],
            class_order=class_order,
        )
        self.check_object_permissions(self.request, task)
        return task

    def list(self, request, *args, **kwargs):
        class_order = self.get_class_order()
        tasks = ClassScopeSelector.tasks_for_order(class_order=class_order)
        return Response(ClassTaskSerializer(tasks, many=True).data)

    def create(self, request, *args, **kwargs):
        class_order = self.get_class_order()
        serializer = ClassTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        assigned_writer = None
        assigned_writer_id = data.get("assigned_writer_id")

        if assigned_writer_id:
                UserModel = get_user_model()
                assigned_writer = UserModel.objects.get(
                    pk=assigned_writer_id
                )

        portal_flags = {
            "requires_portal_work": data.get(
                "requires_portal_work",
                False,
            ),
            "writer_may_upload_to_portal": data.get(
                "writer_may_upload_to_portal",
                True,
            ),
            "writer_may_download_files": data.get(
                "writer_may_download_files",
                True,
            ),
            "portal_submission_required": data.get(
                "portal_submission_required",
                False,
            ),
            "portal_submission_notes": data.get(
                "portal_submission_notes",
                "",
            ),
        }


        task = ClassScopeService.create_manual_task(
            class_order=class_order,
            title=data["title"],
            created_by=request.user,
            description=data.get("description", ""),
            assigned_writer=data.get("assigned_writer"),
            due_at=data.get("due_at"),
            client_visible_notes=data.get("client_visible_notes", ""),
            writer_notes=data.get("writer_notes", ""),
            admin_internal_notes=data.get("admin_internal_notes", ""),
            portal_flags=portal_flags,
        )

        return Response(
            ClassTaskSerializer(task).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None, *args, **kwargs):
        task = self.get_task()
        updated = ClassScopeService.start_task(
            task=task,
            started_by=request.user,
        )
        return Response(ClassTaskSerializer(updated).data)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None, *args, **kwargs):
        task = self.get_task()
        serializer = ClassTaskActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        updated = ClassScopeService.submit_task(
            task=task,
            submitted_by=request.user,
            notes=data.get("notes", ""),
            portal_submitted=data.get("portal_submitted", False),
        )
        return Response(ClassTaskSerializer(updated).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None, *args, **kwargs):
        task = self.get_task()
        serializer = ClassTaskActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        updated = ClassScopeService.complete_task(
            task=task,
            completed_by=request.user,
            notes=data.get("notes", ""),
        )
        return Response(ClassTaskSerializer(updated).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None, *args, **kwargs):
        task = self.get_task()
        serializer = ClassTaskActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        updated = ClassScopeService.cancel_task(
            task=task,
            cancelled_by=request.user,
            reason=data.get("notes", ""),
        )
        return Response(ClassTaskSerializer(updated).data)


class ClassScopeAssessmentViewSet(ClassTenantViewMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, ClassScopePermission]

    def get_class_order(self):
        return ClassOrderSelector.get_for_website(
            website=self.get_website(),
            class_order_id=self.kwargs["class_order_pk"],
        )

    def retrieve(self, request, *args, **kwargs):
        class_order = self.get_class_order()
        assessment = getattr(class_order, "scope_assessment", None)

        if assessment is None:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        return Response(ClassScopeAssessmentSerializer(assessment).data)

    def create(self, request, *args, **kwargs):
        class_order = self.get_class_order()
        serializer = ClassScopeAssessmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        assessment = ClassScopeService.create_or_update_assessment(
            class_order=class_order,
            assessed_by=request.user,
            discussion_posts_count=data.get("discussion_posts_count", 0),
            discussion_responses_count=data.get(
                "discussion_responses_count",
                0,
            ),
            quizzes_count=data.get("quizzes_count", 0),
            exams_count=data.get("exams_count", 0),
            assignments_count=data.get("assignments_count", 0),
            research_papers_count=data.get("research_papers_count", 0),
            term_papers_count=data.get("term_papers_count", 0),
            coursework_items_count=data.get("coursework_items_count", 0),
            projects_count=data.get("projects_count", 0),
            presentations_count=data.get("presentations_count", 0),
            labs_count=data.get("labs_count", 0),
            estimated_hours=data.get(
                "estimated_hours",
                Decimal("0.00"),
            ),
            complexity_level=data.get("complexity_level", "medium"),
            weekly_workload_notes=data.get("weekly_workload_notes", ""),
            grading_weight_notes=data.get("grading_weight_notes", ""),
            client_scope_notes=data.get("client_scope_notes", ""),
            admin_assessment_notes=data.get("admin_assessment_notes", ""),
        )

        return Response(ClassScopeAssessmentSerializer(assessment).data)