# Generated manually for payment disclosure configuration and audit tracking.

import django.conf
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("websites", "0004_add_website_branding_and_payment_disclosure"),
        migrations.swappable_dependency(django.conf.settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="websitebranding",
            name="payment_client_disclosure_text",
            field=models.TextField(
                blank=True,
                help_text="Optional custom disclosure text shown to clients before payment.",
            ),
        ),
        migrations.AddField(
            model_name="websitebranding",
            name="payment_support_contact",
            field=models.CharField(
                blank=True,
                help_text="Billing support contact shown beside payment disclosure.",
                max_length=120,
            ),
        ),
        migrations.AddField(
            model_name="websitebranding",
            name="payment_requires_acknowledgement",
            field=models.BooleanField(
                default=True,
                help_text="Require authenticated clients to acknowledge the disclosure before payment.",
            ),
        ),
        migrations.CreateModel(
            name="PaymentDisclosureAcknowledgement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("processor_display_name", models.CharField(blank=True, max_length=120)),
                ("statement_descriptor", models.CharField(blank=True, max_length=22)),
                ("client_disclosure_text", models.TextField(blank=True)),
                ("support_contact", models.CharField(blank=True, max_length=120)),
                ("context", models.CharField(blank=True, max_length=80)),
                ("reference_type", models.CharField(blank=True, max_length=80)),
                ("reference_id", models.CharField(blank=True, max_length=80)),
                ("shown_at", models.DateTimeField(blank=True, null=True)),
                ("acknowledged_at", models.DateTimeField(blank=True, null=True)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="payment_disclosure_acknowledgements",
                        to=django.conf.settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "website",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payment_disclosure_acknowledgements",
                        to="websites.website",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="paymentdisclosureacknowledgement",
            index=models.Index(fields=["website", "user", "context"], name="websites_pa_website_dd10e2_idx"),
        ),
        migrations.AddIndex(
            model_name="paymentdisclosureacknowledgement",
            index=models.Index(fields=["website", "reference_type", "reference_id"], name="websites_pa_website_278423_idx"),
        ),
        migrations.AddIndex(
            model_name="paymentdisclosureacknowledgement",
            index=models.Index(fields=["shown_at"], name="websites_pa_shown_a_3e6f1e_idx"),
        ),
        migrations.AddIndex(
            model_name="paymentdisclosureacknowledgement",
            index=models.Index(fields=["acknowledged_at"], name="websites_pa_acknowl_a074e2_idx"),
        ),
    ]
