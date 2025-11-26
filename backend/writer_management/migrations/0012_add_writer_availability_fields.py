from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('writer_management', '0011_rename_writer_mana_status_7a8f2d_idx_writer_mana_status_33c805_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='writerprofile',
            name='availability_last_changed',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='writerprofile',
            name='availability_message',
            field=models.CharField(blank=True, default='', max_length=160),
        ),
        migrations.AddField(
            model_name='writerprofile',
            name='is_available_for_auto_assignments',
            field=models.BooleanField(default=True, help_text='Whether the writer is available for instant assignments/queue.'),
        ),
    ]

