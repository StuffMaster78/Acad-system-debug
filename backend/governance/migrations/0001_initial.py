import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Policy",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("tenant_id", models.BigIntegerField(db_index=True, null=True, blank=True)),
                ("version", models.IntegerField(default=1)),
                ("is_active", models.BooleanField(default=True)),
                ("effect", models.CharField(
                    choices=[("allow", "allow"), ("deny", "deny"), ("require_approval", "require_approval")],
                    max_length=30,
                )),
                ("rule", models.JSONField()),
                ("priority", models.IntegerField(default=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"app_label": "governance"},
        ),
        migrations.CreateModel(
            name="PolicyVersion",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("policy_id", models.UUIDField(db_index=True)),
                ("version", models.IntegerField()),
                ("snapshot", models.JSONField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"app_label": "governance"},
        ),
        migrations.CreateModel(
            name="PolicyDecisionLog",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("command_id", models.UUIDField(db_index=True)),
                ("actor_id", models.BigIntegerField()),
                ("tenant_id", models.BigIntegerField()),
                ("decision", models.CharField(max_length=50)),
                ("matched_policies", models.JSONField(default=list)),
                ("risk_score", models.FloatField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"app_label": "governance"},
        ),
    ]
