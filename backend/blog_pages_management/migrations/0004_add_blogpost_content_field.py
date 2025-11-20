# Generated migration for adding content field to BlogPost model
# The previous migration created content as models.Field() which doesn't create a database column
# This migration adds the actual TextField column to the database
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog_pages_management', '0003_add_blogcategory_fields'),
    ]

    operations = [
        # First, try to alter the field from Field() to TextField
        # If that fails because column doesn't exist, we'll add it
        migrations.RunSQL(
            # Add column if it doesn't exist
            sql="ALTER TABLE blog_pages_management_blogpost ADD COLUMN IF NOT EXISTS content TEXT;",
            reverse_sql="ALTER TABLE blog_pages_management_blogpost DROP COLUMN IF EXISTS content;"
        ),
        # Now update the field definition in Django's state
        migrations.AlterField(
            model_name='blogpost',
            name='content',
            field=models.TextField(blank=True, null=True),
        ),
        # Add status field
        migrations.AddField(
            model_name='blogpost',
            name='status',
            field=models.CharField(
                choices=[('draft', 'Draft'), ('scheduled', 'Scheduled'), ('published', 'Published'), ('archived', 'Archived')],
                default='draft',
                help_text='Publication status',
                max_length=20
            ),
        ),
    ]

