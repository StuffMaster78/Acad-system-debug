# Generated migration - Add moderation fields to WriterProgress
# This migration adds fields for admin moderation of progress reports

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_add_external_contact_and_unpaid_override'),
        ('users', '0001_initial'),
    ]

    operations = [
        # Rename text_description to notes
        migrations.RenameField(
            model_name='writerprogress',
            old_name='text_description',
            new_name='notes',
        ),
        # Add moderation fields
        migrations.AddField(
            model_name='writerprogress',
            name='is_withdrawn',
            field=models.BooleanField(default=False, help_text='Whether this progress report has been withdrawn by admin due to policy violations.'),
        ),
        migrations.AddField(
            model_name='writerprogress',
            name='withdrawn_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='withdrawn_progress_reports',
                to='users.user',
                help_text='Admin/superadmin who withdrew this report.'
            ),
        ),
        migrations.AddField(
            model_name='writerprogress',
            name='withdrawn_at',
            field=models.DateTimeField(blank=True, null=True, help_text='When this report was withdrawn.'),
        ),
        migrations.AddField(
            model_name='writerprogress',
            name='withdrawal_reason',
            field=models.TextField(blank=True, null=True, help_text='Reason for withdrawal (e.g., screened words detected).'),
        ),
        migrations.AddField(
            model_name='writerprogress',
            name='contains_screened_words',
            field=models.BooleanField(default=False, help_text='Whether this report contains screened words.'),
        ),
        migrations.AddField(
            model_name='writerprogress',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add indexes
        migrations.AddIndex(
            model_name='writerprogress',
            index=models.Index(fields=['order', '-timestamp'], name='orders_writ_order_i_idx'),
        ),
        migrations.AddIndex(
            model_name='writerprogress',
            index=models.Index(fields=['writer', '-timestamp'], name='orders_writ_writer_idx'),
        ),
        migrations.AddIndex(
            model_name='writerprogress',
            index=models.Index(fields=['is_withdrawn'], name='orders_writ_is_with_idx'),
        ),
    ]

