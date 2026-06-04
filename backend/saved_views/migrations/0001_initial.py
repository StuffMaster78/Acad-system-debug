from __future__ import annotations

import django.db.models.deletion
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
            name="SavedView",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("view_type", models.CharField(
                    choices=[("orders", "Order list"), ("clients", "Client list"), ("writers", "Writer list"),
                              ("payments", "Payments"), ("disputes", "Disputes"), ("analytics", "Analytics"),
                              ("feedback", "Feedback triage"), ("audit", "Audit log"), ("other", "Other")],
                    db_index=True, max_length=30,
                )),
                ("name", models.CharField(max_length=100)),
                ("filters", models.JSONField(default=dict)),
                ("is_default", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="saved_views",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("website", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="saved_views",
                    to="websites.website",
                )),
            ],
            options={"ordering": ["-is_default", "name"]},
        ),
        migrations.AddIndex(
            model_name="savedview",
            index=models.Index(fields=["user", "view_type"], name="saved_views_user_view_idx"),
        ),
        migrations.AlterUniqueTogether(
            name="savedview",
            unique_together={("user", "view_type", "name")},
        ),
    ]
