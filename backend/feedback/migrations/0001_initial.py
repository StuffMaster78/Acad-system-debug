from __future__ import annotations

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("websites", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="FeedbackRequest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("requester_role", models.CharField(max_length=20)),
                (
                    "portal_surface",
                    models.CharField(
                        choices=[
                            ("client", "Client"),
                            ("writer", "Writer"),
                            ("staff", "Staff"),
                        ],
                        max_length=20,
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                (
                    "request_type",
                    models.CharField(
                        choices=[
                            ("feature_request", "Feature Request"),
                            ("improvement", "Improvement"),
                            ("bug_report", "Bug Report"),
                            ("question", "Question"),
                        ],
                        default="feature_request",
                        max_length=20,
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("orders", "Orders"),
                            ("payments", "Payments & Billing"),
                            ("client_experience", "Client Experience"),
                            ("file_delivery", "File Delivery"),
                            ("communication", "Communication"),
                            ("writer_workflow", "Writer Workflow"),
                            ("payout_earnings", "Payout & Earnings"),
                            ("bidding", "Bidding & Queue"),
                            ("workload", "Workload Management"),
                            ("classes", "Classes"),
                            ("special_orders", "Special Orders"),
                            ("cms", "CMS & Content"),
                            ("analytics", "Analytics & Reporting"),
                            ("support_tools", "Support Tools"),
                            ("admin_tools", "Admin Tools"),
                            ("automation", "Automation & SLA"),
                            ("permissions", "Permissions & Roles"),
                            ("bug_report", "Bug Report"),
                            ("other", "Other"),
                        ],
                        default="other",
                        max_length=30,
                    ),
                ),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("low", "Low"),
                            ("medium", "Medium"),
                            ("high", "High"),
                            ("critical", "Critical"),
                        ],
                        default="medium",
                        max_length=10,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("new", "New"),
                            ("triaging", "Triaging"),
                            ("planned", "Planned"),
                            ("in_progress", "In Progress"),
                            ("released", "Released"),
                            ("declined", "Declined"),
                            ("duplicate", "Duplicate"),
                        ],
                        default="new",
                        max_length=20,
                    ),
                ),
                ("upvote_count", models.PositiveIntegerField(default=0)),
                ("linked_order_id", models.PositiveIntegerField(blank=True, null=True)),
                ("linked_ticket_id", models.PositiveIntegerField(blank=True, null=True)),
                ("internal_notes", models.TextField(blank=True, default="")),
                ("public_response", models.TextField(blank=True, default="")),
                ("public_response_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "duplicate_of",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="duplicates",
                        to="feedback.feedbackrequest",
                    ),
                ),
                (
                    "requester",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="feedback_submitted",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "responded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="feedback_responses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "staff_owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="feedback_owned",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "website",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="feedback_requests",
                        to="websites.website",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="FeedbackVote",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "request",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="votes",
                        to="feedback.feedbackrequest",
                    ),
                ),
                (
                    "voter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="feedback_votes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("request", "voter")},
            },
        ),
        migrations.CreateModel(
            name="FeedbackStatusEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("from_status", models.CharField(blank=True, max_length=20)),
                ("to_status", models.CharField(max_length=20)),
                ("note", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "changed_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "request",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="status_history",
                        to="feedback.feedbackrequest",
                    ),
                ),
            ],
            options={
                "ordering": ["created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="feedbackrequest",
            index=models.Index(
                fields=["website", "status"],
                name="feedback_re_website_status_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="feedbackrequest",
            index=models.Index(
                fields=["website", "portal_surface", "status"],
                name="feedback_re_surface_status_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="feedbackrequest",
            index=models.Index(
                fields=["requester", "created_at"],
                name="feedback_re_requester_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="feedbackrequest",
            index=models.Index(
                fields=["status", "category"],
                name="feedback_re_status_category_idx",
            ),
        ),
    ]
