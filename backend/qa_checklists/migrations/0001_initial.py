from __future__ import annotations

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("orders", "0001_initial"),
        ("websites", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="QAChecklistTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("is_default", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="created_qa_templates",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("website", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="qa_checklist_templates",
                    to="websites.website",
                )),
            ],
            options={"ordering": ["-is_default", "name"]},
        ),
        migrations.CreateModel(
            name="QAChecklistItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("category", models.CharField(
                    choices=[("content", "Content quality"), ("formatting", "Formatting & citations"),
                              ("instructions", "Instructions followed"), ("plagiarism", "Originality"),
                              ("delivery", "Delivery & files"), ("other", "Other")],
                    default="content", max_length=20,
                )),
                ("text", models.CharField(max_length=500)),
                ("is_required", models.BooleanField(default=True)),
                ("display_order", models.PositiveSmallIntegerField(default=0)),
                ("template", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="items",
                    to="qa_checklists.qachecklisttemplate",
                )),
            ],
            options={"ordering": ["display_order", "id"]},
        ),
        migrations.CreateModel(
            name="QAChecklistResult",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("checked_items", models.JSONField(default=list)),
                ("verdict", models.CharField(
                    blank=True, max_length=30, null=True,
                    choices=[("passed", "Passed"), ("failed", "Failed — return to writer"),
                              ("passed_with_notes", "Passed with notes")],
                )),
                ("notes", models.TextField(blank=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("order", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="qa_results",
                    to="orders.order",
                )),
                ("reviewer", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="qa_reviews",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("template", models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="results",
                    to="qa_checklists.qachecklisttemplate",
                )),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="qachecklistresult",
            index=models.Index(fields=["order", "reviewer"], name="qa_result_order_reviewer_idx"),
        ),
    ]
