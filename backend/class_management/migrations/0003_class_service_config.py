# Generated manually for tenant-scoped class service configs.

import decimal

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("class_management", "0002_initial"),
        ("websites", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ClassServiceConfig",
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
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=255)),
                ("description", models.TextField(blank=True)),
                (
                    "service_type",
                    models.CharField(default="full_class", max_length=80),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("display_order", models.PositiveIntegerField(default=0)),
                (
                    "pricing_mode",
                    models.CharField(
                        choices=[
                            ("quote", "Quote after review"),
                            ("package", "Package estimate"),
                        ],
                        default="quote",
                        max_length=20,
                    ),
                ),
                (
                    "base_price",
                    models.DecimalField(
                        decimal_places=2,
                        default=decimal.Decimal("0.00"),
                        max_digits=12,
                        validators=[
                            django.core.validators.MinValueValidator(
                                decimal.Decimal("0.00")
                            )
                        ],
                    ),
                ),
                ("currency", models.CharField(default="USD", max_length=10)),
                (
                    "duration_options",
                    models.JSONField(blank=True, default=list),
                ),
                (
                    "workload_options",
                    models.JSONField(blank=True, default=list),
                ),
                ("task_options", models.JSONField(blank=True, default=list)),
                (
                    "required_fields",
                    models.JSONField(blank=True, default=list),
                ),
                ("requires_portal_access", models.BooleanField(default=True)),
                ("allow_installments", models.BooleanField(default=True)),
                (
                    "require_deposit_before_start",
                    models.BooleanField(default=True),
                ),
                (
                    "deposit_percentage",
                    models.DecimalField(
                        decimal_places=2,
                        default=decimal.Decimal("50.00"),
                        max_digits=5,
                        validators=[
                            django.core.validators.MinValueValidator(
                                decimal.Decimal("0.00")
                            )
                        ],
                    ),
                ),
                ("quote_expiry_hours", models.PositiveIntegerField(default=72)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_class_service_configs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "website",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="class_service_configs",
                        to="websites.website",
                    ),
                ),
            ],
            options={
                "ordering": ["display_order", "name"],
            },
        ),
        migrations.AddField(
            model_name="classorder",
            name="class_config",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="class_orders",
                to="class_management.classserviceconfig",
            ),
        ),
        migrations.AddConstraint(
            model_name="classserviceconfig",
            constraint=models.UniqueConstraint(
                fields=("website", "slug"),
                name="unique_class_service_config_slug_per_website",
            ),
        ),
        migrations.AddConstraint(
            model_name="classserviceconfig",
            constraint=models.UniqueConstraint(
                fields=("website", "name"),
                name="unique_class_service_config_name_per_website",
            ),
        ),
        migrations.AddIndex(
            model_name="classserviceconfig",
            index=models.Index(
                fields=["website", "is_active"],
                name="class_manag_website_295020_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="classserviceconfig",
            index=models.Index(
                fields=["website", "slug"],
                name="class_manag_website_3aad64_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="classserviceconfig",
            index=models.Index(
                fields=["display_order"],
                name="class_manag_display_f9d343_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="classorder",
            index=models.Index(
                fields=["website", "class_config"],
                name="class_manag_website_18541c_idx",
            ),
        ),
    ]
