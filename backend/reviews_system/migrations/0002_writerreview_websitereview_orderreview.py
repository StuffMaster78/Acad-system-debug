from __future__ import annotations

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
        ("reviews_system", "0001_initial"),
        ("websites", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="WriterReview",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rating", models.DecimalField(decimal_places=1, max_digits=3)),
                ("comment", models.TextField(blank=True)),
                ("origin", models.CharField(
                    choices=[("client", "Client"), ("staff", "Staff (added on behalf of client)")],
                    default="client", max_length=20,
                )),
                ("is_approved", models.BooleanField(db_index=True, default=False)),
                ("is_flagged", models.BooleanField(db_index=True, default=False)),
                ("is_shadowed", models.BooleanField(db_index=True, default=False)),
                ("submitted_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reviewer", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="writer_reviews_given",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("writer", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="writer_reviews_received",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("website", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="writer_reviews",
                    to="websites.website",
                )),
            ],
            options={"ordering": ["-submitted_at"]},
        ),
        migrations.CreateModel(
            name="WebsiteReview",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rating", models.DecimalField(decimal_places=1, max_digits=3)),
                ("comment", models.TextField(blank=True)),
                ("origin", models.CharField(
                    choices=[("client", "Client"), ("staff", "Staff")],
                    default="client", max_length=20,
                )),
                ("is_approved", models.BooleanField(db_index=True, default=False)),
                ("is_flagged", models.BooleanField(db_index=True, default=False)),
                ("is_shadowed", models.BooleanField(db_index=True, default=False)),
                ("submitted_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reviewer", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="website_reviews",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("website", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="website_reviews",
                    to="websites.website",
                )),
            ],
            options={"ordering": ["-submitted_at"]},
        ),
        migrations.CreateModel(
            name="OrderReview",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rating", models.DecimalField(decimal_places=1, max_digits=3)),
                ("comment", models.TextField(blank=True)),
                ("origin", models.CharField(
                    choices=[("client", "Client"), ("staff", "Staff")],
                    default="client", max_length=20,
                )),
                ("is_approved", models.BooleanField(db_index=True, default=False)),
                ("is_flagged", models.BooleanField(db_index=True, default=False)),
                ("is_shadowed", models.BooleanField(db_index=True, default=False)),
                ("submitted_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reviewer", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="order_reviews",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("order", models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="client_review",
                    to="orders.order",
                )),
                ("writer", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="order_reviews_received",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("website", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="order_reviews",
                    to="websites.website",
                )),
            ],
            options={"ordering": ["-submitted_at"]},
        ),
        migrations.AddIndex(
            model_name="writerreview",
            index=models.Index(fields=["writer", "is_approved"], name="reviews_wr_writer_idx"),
        ),
        migrations.AddIndex(
            model_name="writerreview",
            index=models.Index(fields=["website", "submitted_at"], name="reviews_wr_website_idx"),
        ),
        migrations.AddIndex(
            model_name="websitereview",
            index=models.Index(fields=["website", "is_approved"], name="reviews_wsr_website_idx"),
        ),
        migrations.AddIndex(
            model_name="orderreview",
            index=models.Index(fields=["writer", "is_approved"], name="reviews_or_writer_idx"),
        ),
        migrations.AddIndex(
            model_name="orderreview",
            index=models.Index(fields=["website", "submitted_at"], name="reviews_or_website_idx"),
        ),
        migrations.AlterUniqueTogether(
            name="websitereview",
            unique_together={("reviewer", "website")},
        ),
    ]
