from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("admin_management", "0002_initial"),
        ("websites", "0005_payment_disclosure_acknowledgement"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="OperationsCommandItemState",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("item_id", models.CharField(max_length=180, unique=True)),
                ("domain", models.CharField(max_length=80)),
                ("entity_type", models.CharField(max_length=80)),
                ("entity_id", models.PositiveIntegerField(blank=True, null=True)),
                ("entity_label", models.CharField(blank=True, max_length=255)),
                ("status", models.CharField(choices=[("active", "Active"), ("acknowledged", "Acknowledged"), ("snoozed", "Snoozed"), ("resolved", "Resolved")], db_index=True, default="active", max_length=30)),
                ("note", models.TextField(blank=True)),
                ("snoozed_until", models.DateTimeField(blank=True, null=True)),
                ("assigned_at", models.DateTimeField(blank=True, null=True)),
                ("acknowledged_at", models.DateTimeField(blank=True, null=True)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("acknowledged_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="acknowledged_operations_items", to=settings.AUTH_USER_MODEL)),
                ("assigned_to", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assigned_operations_items", to=settings.AUTH_USER_MODEL)),
                ("resolved_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="resolved_operations_items", to=settings.AUTH_USER_MODEL)),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="updated_operations_items", to=settings.AUTH_USER_MODEL)),
                ("website", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="operations_command_item_states", to="websites.website")),
            ],
            options={
                "ordering": ["-updated_at"],
            },
        ),
        migrations.AddIndex(
            model_name="operationscommanditemstate",
            index=models.Index(fields=["status", "snoozed_until"], name="admin_manag_status_46a32d_idx"),
        ),
        migrations.AddIndex(
            model_name="operationscommanditemstate",
            index=models.Index(fields=["assigned_to", "status"], name="admin_manag_assigne_7798ac_idx"),
        ),
        migrations.AddIndex(
            model_name="operationscommanditemstate",
            index=models.Index(fields=["website", "status"], name="admin_manag_website_25db05_idx"),
        ),
        migrations.AddIndex(
            model_name="operationscommanditemstate",
            index=models.Index(fields=["domain", "status"], name="admin_manag_domain_079104_idx"),
        ),
    ]
