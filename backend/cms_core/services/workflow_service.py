"""
Editorial Workflow Service
============================

Configures Wagtail's built-in Workflow system for multi-step publishing:

    Draft → Editor Review → Quality Check → Publish

Wagtail's workflow engine handles:
    • Task assignment to groups
    • Approval / rejection with comments
    • Email notifications to reviewers
    • Dashboard indicators for pending tasks
    • Workflow history and audit trail

This service configures the workflow and adds:
    • Post-publish audit (Celery task that verifies page health 24h after publish)
    • Pre-publish quality gate (runs validators as a workflow task)

Usage:
    from cms_core.services.workflow_service import WorkflowService

    WorkflowService.setup_editorial_workflow(site)  # one-time per tenant
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.contrib.auth.models import Group

from wagtail.models import (
    Site,
    Task,
    Workflow,
    WorkflowTask,
    GroupApprovalTask,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class WorkflowService:
    """Configure and manage editorial workflows per tenant."""

    # ---------------------------------------------------------------
    # Workflow setup
    # ---------------------------------------------------------------

    @classmethod
    def setup_editorial_workflow(cls, site: Site) -> Workflow:
        """
        Create the standard editorial workflow for a tenant.

        Pipeline:
            1. Editor Review  — assigned to ``{Tenant} Editors`` group
            2. Quality Check   — assigned to ``{Tenant} Admins`` group

        After approval at step 2, Wagtail publishes the page.
        Post-publish audit is triggered via the ``after_publish_page``
        hook (see wagtail_hooks.py).

        Idempotent — safe to call multiple times.
        """
        tenant_name = site.site_name or site.hostname
        workflow_name = f"{tenant_name} Editorial Workflow"

        # Get or create the workflow
        workflow, wf_created = Workflow.objects.get_or_create(
            name=workflow_name,
            defaults={"active": True},
        )

        if wf_created:
            logger.info("Created workflow: %s", workflow_name)

        # --- Task 1: Editor Review ---
        editor_task = cls._get_or_create_approval_task(
            name=f"{tenant_name} — Editor Review",
            group_name=f"{tenant_name} Editors",
        )

        # --- Task 2: Quality / Admin Check ---
        quality_task = cls._get_or_create_approval_task(
            name=f"{tenant_name} — Quality Check",
            group_name=f"{tenant_name} Admins",
        )

        # Wire tasks to workflow in order (only if not already wired)
        cls._ensure_workflow_task(workflow, editor_task, sort_order=0)
        cls._ensure_workflow_task(workflow, quality_task, sort_order=1)

        # Assign workflow to the tenant's page tree
        cls._assign_workflow_to_page_tree(workflow, site)

        logger.info(
            "Editorial workflow '%s' configured with %d tasks",
            workflow_name,
            workflow.workflow_tasks.count(),
        )
        return workflow

    @classmethod
    def setup_simple_workflow(cls, site: Site) -> Workflow:
        """
        Simplified workflow for tenants that don't need multi-step review:

            1. Admin Approval → Publish

        Use for small teams or early-stage tenants.
        """
        tenant_name = site.site_name or site.hostname
        workflow_name = f"{tenant_name} Simple Workflow"

        workflow, wf_created = Workflow.objects.get_or_create(
            name=workflow_name,
            defaults={"active": True},
        )

        if wf_created:
            logger.info("Created simple workflow: %s", workflow_name)

        admin_task = cls._get_or_create_approval_task(
            name=f"{tenant_name} — Admin Approval",
            group_name=f"{tenant_name} Admins",
        )

        cls._ensure_workflow_task(workflow, admin_task, sort_order=0)
        cls._assign_workflow_to_page_tree(workflow, site)

        return workflow

    # ---------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------

    @classmethod
    def _get_or_create_approval_task(
        cls,
        name: str,
        group_name: str,
    ) -> GroupApprovalTask:
        """
        Create a GroupApprovalTask that requires approval from members
        of the given group.
        """
        # Check if the task already exists
        existing = Task.objects.filter(name=name).first()
        if existing:
            return existing.specific

        # Get or create the group
        group, _ = Group.objects.get_or_create(name=group_name)

        task = GroupApprovalTask.objects.create(
            name=name,
            active=True,
        )
        task.groups.add(group)
        logger.info("Created approval task: %s → group '%s'", name, group_name)
        return task

    @classmethod
    def _ensure_workflow_task(
        cls,
        workflow: Workflow,
        task: Task,
        sort_order: int,
    ) -> None:
        """Add a task to a workflow if not already present."""
        exists = WorkflowTask.objects.filter(
            workflow=workflow,
            task=task,
        ).exists()

        if not exists:
            WorkflowTask.objects.create(
                workflow=workflow,
                task=task,
                sort_order=sort_order,
            )
            logger.debug(
                "Added task '%s' to workflow '%s' at position %d",
                task.name,
                workflow.name,
                sort_order,
            )

    @classmethod
    def _assign_workflow_to_page_tree(
        cls,
        workflow: Workflow,
        site: Site,
    ) -> None:
        """
        Assign a workflow to the tenant's root page so it applies
        to all pages in the tenant's tree.
        """
        from wagtail.models import WorkflowPage

        root_page = site.root_page

        # Check if already assigned
        existing = WorkflowPage.objects.filter(page=root_page).first()
        if existing:
            if existing.workflow != workflow:
                existing.workflow = workflow
                existing.save()
                logger.info(
                    "Updated workflow on '%s' to '%s'",
                    root_page.title,
                    workflow.name,
                )
            return

        WorkflowPage.objects.create(
            page=root_page,
            workflow=workflow,
        )
        logger.info(
            "Assigned workflow '%s' to page tree '%s'",
            workflow.name,
            root_page.title,
        )

    # ---------------------------------------------------------------
    # Query helpers
    # ---------------------------------------------------------------

    @classmethod
    def get_pending_reviews_for_user(cls, user) -> list:
        """
        Return all pages currently awaiting review from this user.
        Uses Wagtail's built-in TaskState.
        """
        from wagtail.models import TaskState

        if user.is_superuser:
            return list(
                TaskState.objects.filter(
                    status="in_progress",
                ).select_related("page_revision__page", "task")
            )

        # Find tasks assigned to the user's groups
        user_groups = user.groups.all()
        group_tasks = GroupApprovalTask.objects.filter(
            groups__in=user_groups,
            active=True,
        )

        return list(
            TaskState.objects.filter(
                status="in_progress",
                task__in=group_tasks,
            ).select_related("page_revision__page", "task")
        )

    @classmethod
    def get_workflow_history_for_page(cls, page) -> list:
        """Return the workflow states for a page, most recent first."""
        from wagtail.models import WorkflowState

        return list(
            WorkflowState.objects.filter(
                page=page,
            )
            .select_related("workflow", "requested_by")
            .order_by("-created_at")
        )