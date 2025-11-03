# Generated migration for EditorNotification missing fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('editor_management', '0006_add_editortaskassignment_fields'),
        ('orders', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='editornotification',
            name='related_order',
            field=models.ForeignKey(blank=True, help_text='Related order, if applicable.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='editor_notifications', to='orders.order'),
        ),
        migrations.AddField(
            model_name='editornotification',
            name='related_task',
            field=models.ForeignKey(blank=True, help_text='Related task assignment, if applicable.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notifications', to='editor_management.editortaskassignment'),
        ),
        migrations.AddField(
            model_name='editornotification',
            name='notification_type',
            field=models.CharField(choices=[('info', 'Info'), ('task_assigned', 'Task Assigned'), ('task_claimed', 'Task Claimed'), ('reminder', 'Reminder'), ('urgent', 'Urgent')], default='info', help_text='Type of notification.', max_length=50),
        ),
        migrations.AddIndex(
            model_name='editornotification',
            index=models.Index(fields=['editor', 'is_read', 'created_at'], name='editor_mana_editor__idx'),
        ),
    ]

