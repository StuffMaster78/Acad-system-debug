# Generated migration for EditorTaskAssignment missing fields
from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('editor_management', '0005_add_all_missing_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='editortaskassignment',
            name='assignment_type',
            field=models.CharField(choices=[('auto', 'Auto-Assigned'), ('manual', 'Manually Assigned'), ('claimed', 'Self-Claimed')], default='auto', help_text='How this task was assigned.', max_length=20),
        ),
        migrations.AddField(
            model_name='editortaskassignment',
            name='assigned_by',
            field=models.ForeignKey(blank=True, help_text='User who assigned this task (admin/system for auto-assigned).', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='editor_assignments_made', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='editortaskassignment',
            name='assigned_at',
            field=models.DateTimeField(auto_now_add=True, help_text='When this task was assigned.'),
        ),
        migrations.AddField(
            model_name='editortaskassignment',
            name='review_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('in_review', 'In Review'), ('completed', 'Completed'), ('rejected', 'Rejected'), ('unclaimed', 'Unclaimed')], default='pending', help_text='The current review status of the task.', max_length=20),
        ),
        migrations.AddField(
            model_name='editortaskassignment',
            name='started_at',
            field=models.DateTimeField(blank=True, help_text='When the editor started reviewing this task.', null=True),
        ),
        migrations.AddField(
            model_name='editortaskassignment',
            name='reviewed_at',
            field=models.DateTimeField(blank=True, help_text='Timestamp when the task was reviewed.', null=True),
        ),
        migrations.AddField(
            model_name='editortaskassignment',
            name='notes',
            field=models.TextField(blank=True, help_text='Additional notes or feedback from the editor.', null=True),
        ),
        migrations.AddField(
            model_name='editortaskassignment',
            name='editor_rating',
            field=models.PositiveIntegerField(blank=True, help_text='Quality rating given by admin/superadmin (1-5).', null=True),
        ),
        migrations.AddIndex(
            model_name='editortaskassignment',
            index=models.Index(fields=['assigned_editor', 'review_status'], name='editor_mana_assigne_idx'),
        ),
        migrations.AddIndex(
            model_name='editortaskassignment',
            index=models.Index(fields=['review_status', 'assigned_at'], name='editor_mana_review__idx'),
        ),
        migrations.AddIndex(
            model_name='editortaskassignment',
            index=models.Index(fields=['order'], name='editor_mana_order_id_idx'),
        ),
    ]

