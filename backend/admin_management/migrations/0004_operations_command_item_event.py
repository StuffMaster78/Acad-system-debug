from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("admin_management", "0003_operations_command_item_state"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="OperationsCommandItemEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(max_length=40)),
                ("note", models.TextField(blank=True)),
                ("from_status", models.CharField(blank=True, max_length=30)),
                ("to_status", models.CharField(blank=True, max_length=30)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("actor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="operations_command_events", to=settings.AUTH_USER_MODEL)),
                ("state", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="events", to="admin_management.operationscommanditemstate")),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="operationscommanditemevent",
            index=models.Index(fields=["state", "created_at"], name="admin_manag_state_i_7a7f11_idx"),
        ),
        migrations.AddIndex(
            model_name="operationscommanditemevent",
            index=models.Index(fields=["actor", "created_at"], name="admin_manag_actor_i_a3d6b9_idx"),
        ),
        migrations.AddIndex(
            model_name="operationscommanditemevent",
            index=models.Index(fields=["action", "created_at"], name="admin_manag_action__2f193c_idx"),
        ),
    ]
