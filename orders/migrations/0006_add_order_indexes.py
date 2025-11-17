# Generated migration - Add performance indexes to Order model
# This migration adds indexes for commonly filtered and queried fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_add_progress_moderation_fields'),
    ]

    operations = [
        # Single field indexes for common filters
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['status'], name='orders_order_status_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['is_paid'], name='orders_order_is_paid_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['created_at'], name='orders_order_created_at_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['client'], name='orders_order_client_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['assigned_writer'], name='orders_order_assigned_writer_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['website'], name='orders_order_website_idx'),
        ),
        # Composite indexes for common query patterns
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['status', 'is_paid'], name='orders_order_status_paid_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['client', 'status'], name='orders_order_client_status_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['assigned_writer', 'status'], name='orders_order_writer_status_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['website', 'status'], name='orders_order_website_status_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['status', 'created_at'], name='orders_order_status_created_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['is_paid', 'created_at'], name='orders_order_paid_created_idx'),
        ),
    ]

