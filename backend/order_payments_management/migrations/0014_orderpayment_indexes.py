from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("order_payments_management", "0013_add_custom_payment_link_to_invoice"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="orderpayment",
            index=models.Index(fields=["status", "created_at"], name="orderpay_status_created_idx"),
        ),
        migrations.AddIndex(
            model_name="orderpayment",
            index=models.Index(fields=["order", "status"], name="orderpay_order_status_idx"),
        ),
    ]
