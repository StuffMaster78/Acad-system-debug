# Generated migration - Add indexes for writer dashboard query patterns
# This migration adds indexes to optimize writer-specific queries

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0019_orderdraft_orderpreset_revisionrequest'),
    ]

    operations = [
        # Add preferred_writer index
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['preferred_writer'], name='orders_orde_preferred_writer_idx'),
        ),
        # Writer dashboard specific composite indexes
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['assigned_writer', 'status', 'created_at'], name='orders_orde_writer_status_created_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['assigned_writer', 'created_at'], name='orders_orde_writer_created_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['website', 'status', 'is_paid', 'assigned_writer'], name='orders_orde_website_status_paid_writer_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['website', 'status', 'is_paid', 'preferred_writer'], name='orders_orde_website_status_paid_pref_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['status', 'assigned_writer', 'is_deleted'], name='orders_orde_status_writer_deleted_idx'),
        ),
    ]

