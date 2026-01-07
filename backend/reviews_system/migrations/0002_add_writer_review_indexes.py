# Generated migration - Add indexes for writer review queries
# This migration adds indexes to optimize writer review queries in dashboard

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews_system', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='writerreview',
            index=models.Index(fields=['writer', 'submitted_at'], name='reviews_writerreview_writer_submitted_idx'),
        ),
        migrations.AddIndex(
            model_name='writerreview',
            index=models.Index(fields=['website', 'submitted_at'], name='reviews_writerreview_website_submitted_idx'),
        ),
        migrations.AddIndex(
            model_name='writerreview',
            index=models.Index(fields=['writer', 'website', 'submitted_at'], name='reviews_writerreview_writer_website_submitted_idx'),
        ),
    ]

