from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("privacy", "0001_cookie_consent_record"),
        ("websites", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExitIntentPopupConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_enabled", models.BooleanField(default=False)),
                ("trigger", models.CharField(choices=[("exit_intent", "Exit intent"), ("delay", "Time delay"), ("scroll_depth", "Scroll depth")], default="exit_intent", max_length=32)),
                ("title", models.CharField(default="Before you go", max_length=140)),
                ("body", models.TextField(default="Need help choosing the right service? Get a quick quote and see your options before you leave.")),
                ("primary_cta_label", models.CharField(default="Get a quick quote", max_length=80)),
                ("primary_cta_url", models.CharField(default="/quote", max_length=255)),
                ("secondary_cta_label", models.CharField(blank=True, default="Maybe later", max_length=80)),
                ("image_url", models.URLField(blank=True, default="")),
                ("show_on_paths", models.JSONField(blank=True, default=list, help_text="Path prefixes where the popup may show. Empty means all public pages.")),
                ("suppress_on_paths", models.JSONField(blank=True, default=list, help_text="Path prefixes where the popup must not show.")),
                ("delay_seconds", models.PositiveIntegerField(default=15)),
                ("scroll_depth_percent", models.PositiveIntegerField(default=65)),
                ("cooldown_hours", models.PositiveIntegerField(default=24)),
                ("max_shows_per_session", models.PositiveIntegerField(default=1)),
                ("requires_marketing_consent", models.BooleanField(default=False, help_text="When enabled, only show after the visitor accepts marketing cookies.")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("website", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="exit_intent_popup_config", to="websites.website")),
            ],
            options={
                "verbose_name": "Exit intent popup config",
                "verbose_name_plural": "Exit intent popup configs",
            },
        ),
    ]
