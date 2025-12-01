from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("websites", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="websitestaticpage",
            name="version",
            field=models.PositiveIntegerField(
                default=1,
                help_text="Version number for this page (useful for Terms & Conditions).",
            ),
        ),
        migrations.CreateModel(
            name="WebsiteTermsAcceptance",
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
                (
                    "terms_version",
                    models.PositiveIntegerField(
                        help_text="Version number of the terms page when accepted."
                    ),
                ),
                (
                    "accepted_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="When the user accepted the terms.",
                    ),
                ),
                (
                    "ip_address",
                    models.GenericIPAddressField(
                        blank=True,
                        help_text="IP address from which terms were accepted.",
                        null=True,
                    ),
                ),
                (
                    "user_agent",
                    models.TextField(
                        blank=True,
                        help_text="User agent string at the time of acceptance.",
                        null=True,
                    ),
                ),
                (
                    "static_page",
                    models.ForeignKey(
                        help_text="The static page (usually slug='terms') that was accepted.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="terms_acceptances",
                        to="websites.websitestaticpage",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="terms_acceptances",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "website",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="terms_acceptances",
                        to="websites.website",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(fields=["website", "user"], name="websites_we_website__idx"),
                    models.Index(
                        fields=["website", "static_page", "terms_version"],
                        name="websites_we_website_1b56c4_idx",
                    ),
                ],
                "unique_together": {("website", "user", "static_page", "terms_version")},
            },
        ),
    ]


