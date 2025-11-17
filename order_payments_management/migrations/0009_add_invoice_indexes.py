# Generated manually for Invoice model index optimizations
# Generated on 2024-12-19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_payments_management', '0008_update_invoice_model_complete'),
    ]

    operations = [
        # Add single field indexes for commonly filtered fields
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['is_paid'], name='order_payme_is_paid_single_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['created_at'], name='order_payme_created_at_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['client'], name='order_payme_client_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['website'], name='order_payme_website_single_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['due_date'], name='order_payme_due_date_idx'),
        ),
        # Add composite indexes for common query patterns
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['client', 'is_paid'], name='order_payme_client_paid_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['website', 'created_at'], name='order_payme_website_created_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['is_paid', 'created_at'], name='order_payme_paid_created_idx'),
        ),
    ]

