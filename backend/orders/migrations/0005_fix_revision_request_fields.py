from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0004_rename_orders_orde_order_i_idx_orders_orde_order_i_d0cfbe_idx"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="orderrevisionrequest",
            name="instructions",
        ),
        migrations.RemoveField(
            model_name="orderrevisionrequest",
            name="client_notes",
        ),
        migrations.AddField(
            model_name="orderrevisionrequest",
            name="reason",
            field=models.CharField(
                default="",
                max_length=2000,
                help_text="Brief reason for the revision request.",
            ),
        ),
        migrations.AddField(
            model_name="orderrevisionrequest",
            name="scope_summary",
            field=models.TextField(
                default="",
                help_text="Detailed description of what needs to change.",
            ),
        ),
        migrations.AddField(
            model_name="orderrevisionrequest",
            name="approved_at",
            field=models.DateTimeField(
                null=True,
                blank=True,
                help_text="When the revision request was approved.",
            ),
        ),
    ]
