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
            name="ChangelogEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("portal_surface", models.CharField(
                    choices=[("client", "Client portal"), ("writer", "Writer portal"),
                              ("staff", "Staff portal"), ("public", "Public (all)")],
                    db_index=True, default="public", max_length=20,
                )),
                ("entry_type", models.CharField(
                    choices=[("feature", "New feature"), ("improvement", "Improvement"),
                              ("fix", "Bug fix"), ("maintenance", "Maintenance"), ("notice", "Notice")],
                    default="feature", max_length=20,
                )),
                ("version", models.CharField(blank=True, max_length=30)),
                ("title", models.CharField(max_length=255)),
                ("body", models.TextField()),
                ("is_published", models.BooleanField(db_index=True, default=False)),
                ("is_pinned", models.BooleanField(default=False)),
                ("published_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="changelog_entries",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("website", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="changelog_entries",
                    to="websites.website",
                )),
            ],
            options={"ordering": ["-is_pinned", "-published_at", "-created_at"]},
        ),
        migrations.AddIndex(
            model_name="changelogentry",
            index=models.Index(
                fields=["portal_surface", "is_published", "-published_at"],
                name="changelog_surface_pub_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="changelogentry",
            index=models.Index(
                fields=["website", "portal_surface", "is_published"],
                name="changelog_website_surface_idx",
            ),
        ),
    ]
