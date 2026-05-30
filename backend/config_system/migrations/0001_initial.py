import uuid
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ConfigItem",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("key", models.CharField(db_index=True, max_length=255)),
                ("value", models.JSONField()),
                ("scope", models.CharField(
                    choices=[("global", "Global"), ("tenant", "Tenant"), ("website", "Website"), ("user", "User")],
                    db_index=True, default="global", max_length=20,
                )),
                ("environment", models.CharField(db_index=True, default="prod", max_length=32)),
                ("website_id", models.BigIntegerField(blank=True, db_index=True, null=True)),
                ("tenant_id", models.BigIntegerField(blank=True, db_index=True, null=True)),
                ("user_id", models.BigIntegerField(blank=True, db_index=True, null=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("last_modified_at", models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ("notes", models.TextField(blank=True, default="")),
                ("created_by", models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name="created_configs", to=settings.AUTH_USER_MODEL,
                )),
                ("updated_by", models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name="updated_configs", to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={"db_table": "config_items", "ordering": ("key", "-updated_at")},
        ),
        migrations.CreateModel(
            name="ConfigAuditLog",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("key", models.CharField(db_index=True, max_length=255)),
                ("scope", models.CharField(db_index=True, max_length=20)),
                ("environment", models.CharField(db_index=True, max_length=32)),
                ("action", models.CharField(
                    choices=[("create", "Create"), ("update", "Update"), ("delete", "Delete")],
                    db_index=True, max_length=20,
                )),
                ("old_value", models.JSONField(blank=True, null=True)),
                ("new_value", models.JSONField(blank=True, null=True)),
                ("reason", models.TextField(blank=True, default="")),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("config_item", models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name="audit_logs", to="config_system.configitem",
                )),
                ("changed_by", models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name="config_changes", to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={"db_table": "config_audit_logs", "ordering": ("-created_at",)},
        ),
        migrations.AddIndex(
            model_name="configitem",
            index=models.Index(fields=["key", "scope", "is_active"], name="config_core_lookup_idx"),
        ),
        migrations.AddIndex(
            model_name="configitem",
            index=models.Index(fields=["key", "tenant_id", "is_active"], name="config_tenant_lookup_idx"),
        ),
        migrations.AddIndex(
            model_name="configitem",
            index=models.Index(fields=["key", "website_id", "is_active"], name="config_website_lookup_idx"),
        ),
        migrations.AddIndex(
            model_name="configitem",
            index=models.Index(fields=["key", "user_id", "is_active"], name="config_user_lookup_idx"),
        ),
        migrations.AddIndex(
            model_name="configitem",
            index=models.Index(fields=["environment", "is_active"], name="config_env_lookup_idx"),
        ),
        migrations.AddConstraint(
            model_name="configitem",
            constraint=models.UniqueConstraint(
                condition=models.Q(is_active=True),
                fields=["key", "scope", "environment", "website_id", "tenant_id", "user_id"],
                name="unique_active_config_scope",
            ),
        ),
        migrations.AddIndex(
            model_name="configauditlog",
            index=models.Index(fields=["key", "created_at"], name="config_audit_key_idx"),
        ),
        migrations.AddIndex(
            model_name="configauditlog",
            index=models.Index(fields=["action", "created_at"], name="config_audit_action_idx"),
        ),
    ]
