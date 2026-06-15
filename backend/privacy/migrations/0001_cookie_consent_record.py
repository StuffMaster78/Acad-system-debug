from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("websites", "0007_writerscreek_website"),
    ]

    operations = [
        migrations.CreateModel(
            name="CookieConsentRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("anonymous_id", models.UUIDField(db_index=True, default=uuid.uuid4)),
                ("consent_version", models.CharField(default="2026-06-15", max_length=40)),
                ("policy_version", models.CharField(default="2026-06-15", max_length=40)),
                ("necessary", models.BooleanField(default=True)),
                ("preferences", models.BooleanField(default=False)),
                ("analytics", models.BooleanField(default=False)),
                ("marketing", models.BooleanField(default=False)),
                ("source", models.CharField(choices=[("banner", "Cookie banner"), ("settings", "Cookie settings"), ("footer", "Footer link"), ("api", "API")], default="banner", max_length=20)),
                ("source_host", models.CharField(blank=True, max_length=255)),
                ("ip_hash", models.CharField(blank=True, max_length=64)),
                ("user_agent_hash", models.CharField(blank=True, max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="cookie_consent_records", to=settings.AUTH_USER_MODEL)),
                ("website", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="cookie_consent_records", to="websites.website")),
            ],
            options={
                "ordering": ["-created_at", "-id"],
                "indexes": [
                    models.Index(fields=["website", "anonymous_id", "-created_at"], name="privacy_coo_website_eabf8d_idx"),
                    models.Index(fields=["user", "-created_at"], name="privacy_coo_user_id_c85e3f_idx"),
                    models.Index(fields=["revoked_at"], name="privacy_coo_revoked_f16a4d_idx"),
                ],
            },
        ),
    ]
