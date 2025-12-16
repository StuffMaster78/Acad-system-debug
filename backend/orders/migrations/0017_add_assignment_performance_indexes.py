# Generated migration - Add performance indexes for assignment-related queries
# This migration adds indexes to optimize assignment service queries

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0016_order_delete_reason_order_deleted_at_and_more'),
    ]

    operations = [
        # Indexes for assignment-related queries
        # Status + assigned_writer (for finding active assignments by writer)
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['status', 'assigned_writer'], name='orders_orde_status_assigne_idx'),
        ),
        # Status + website + is_deleted (for filtering available orders by website)
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['status', 'website', 'is_deleted'], name='orders_orde_status_website_deleted_idx'),
        ),
        # Subject + status (for subject-based matching)
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['subject', 'status'], name='orders_orde_subject_status_idx'),
        ),
        # Paper type + status (for paper type matching)
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['paper_type', 'status'], name='orders_orde_paper_type_status_idx'),
        ),
        # Assigned writer + status + is_deleted (for writer workload queries)
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['assigned_writer', 'status', 'is_deleted'], name='orders_orde_writer_status_deleted_idx'),
        ),
        # Website + status + created_at (for assignment queue queries)
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['website', 'status', 'created_at'], name='orders_orde_website_status_created_idx'),
        ),
        # Rating index for writer rating calculations (composite with status)
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['assigned_writer', 'status', 'rating'], name='orders_orde_writer_status_rating_idx'),
        ),
    ]

