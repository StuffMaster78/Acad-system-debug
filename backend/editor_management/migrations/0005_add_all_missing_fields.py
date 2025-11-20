# Generated migration for all missing EditorProfile, EditorPerformance, and EditorActionLog fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('editor_management', '0004_add_editor_profile_fields'),
        ('orders', '0002_initial'),
    ]

    operations = [
        # EditorPerformance fields
        migrations.AddField(
            model_name='editorperformance',
            name='average_review_time',
            field=models.DurationField(blank=True, help_text='Average time taken to review tasks.', null=True),
        ),
        migrations.AddField(
            model_name='editorperformance',
            name='total_orders_reviewed',
            field=models.PositiveIntegerField(default=0, help_text='Total number of orders reviewed by the editor.'),
        ),
        migrations.AddField(
            model_name='editorperformance',
            name='late_reviews',
            field=models.PositiveIntegerField(default=0, help_text='Number of reviews completed past the deadline.'),
        ),
        migrations.AddField(
            model_name='editorperformance',
            name='average_quality_score',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Average quality score given by admin.', max_digits=3, null=True),
        ),
        migrations.AddField(
            model_name='editorperformance',
            name='revisions_requested_count',
            field=models.PositiveIntegerField(default=0, help_text='Total number of revisions requested.'),
        ),
        migrations.AddField(
            model_name='editorperformance',
            name='approvals_count',
            field=models.PositiveIntegerField(default=0, help_text='Total number of orders approved for delivery.'),
        ),
        migrations.AddField(
            model_name='editorperformance',
            name='last_calculated_at',
            field=models.DateTimeField(blank=True, help_text='When performance metrics were last calculated.', null=True),
        ),
        # EditorActionLog fields
        migrations.AddField(
            model_name='editoractionlog',
            name='action_type',
            field=models.CharField(choices=[('claimed_task', 'Claimed Task'), ('started_review', 'Started Review'), ('submitted_review', 'Submitted Review'), ('completed_task', 'Completed Task'), ('rejected_task', 'Rejected Task'), ('unclaimed_task', 'Unclaimed Task')], default='completed_task', help_text='Type of action performed.', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='editoractionlog',
            name='action',
            field=models.CharField(default='Action performed', help_text="Description of the action performed (e.g., 'Reviewed Order').", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='editoractionlog',
            name='related_order',
            field=models.ForeignKey(blank=True, help_text='The order associated with this action.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='editor_actions', to='orders.order'),
        ),
        migrations.AddField(
            model_name='editoractionlog',
            name='related_task',
            field=models.ForeignKey(blank=True, help_text='The task assignment associated with this action.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='action_logs', to='editor_management.editortaskassignment'),
        ),
        migrations.AddField(
            model_name='editoractionlog',
            name='metadata',
            field=models.JSONField(blank=True, default=dict, help_text='Additional metadata about the action.'),
        ),
        migrations.AddField(
            model_name='editoractionlog',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, help_text='Timestamp of the action.'),
        ),
        # Add indexes for EditorActionLog
        migrations.AddIndex(
            model_name='editoractionlog',
            index=models.Index(fields=['editor', 'timestamp'], name='editor_mana_editor__idx'),
        ),
        migrations.AddIndex(
            model_name='editoractionlog',
            index=models.Index(fields=['action_type', 'timestamp'], name='editor_mana_action__idx'),
        ),
    ]

