# Generated migration for all missing EditorProfile, EditorPerformance, and EditorActionLog fields
from django.db import migrations, models
import django.db.models.deletion


def add_fields_if_not_exists(apps, schema_editor):
    """Add fields only if they don't already exist in the database."""
    db_alias = schema_editor.connection.alias
    
    # Check and add EditorPerformance fields
    EditorPerformance = apps.get_model('editor_management', 'EditorPerformance')
    table_name = EditorPerformance._meta.db_table
    
    with schema_editor.connection.cursor() as cursor:
        # Get existing columns
        cursor.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
        """)
        existing_columns = {row[0] for row in cursor.fetchall()}
        
        # Add average_review_time if it doesn't exist
        if 'average_review_time' not in existing_columns:
            cursor.execute(f"""
                ALTER TABLE {table_name} 
                ADD COLUMN average_review_time interval NULL
            """)
        
        # Add other fields if they don't exist
        fields_to_add = [
            ('total_orders_reviewed', 'integer DEFAULT 0 NOT NULL'),
            ('late_reviews', 'integer DEFAULT 0 NOT NULL'),
            ('average_quality_score', 'numeric(3,2) NULL'),
            ('revisions_requested_count', 'integer DEFAULT 0 NOT NULL'),
            ('approvals_count', 'integer DEFAULT 0 NOT NULL'),
            ('last_calculated_at', 'timestamp with time zone NULL'),
        ]
        
        for field_name, field_type in fields_to_add:
            if field_name not in existing_columns:
                cursor.execute(f"""
                    ALTER TABLE {table_name} 
                    ADD COLUMN {field_name} {field_type}
                """)
        
        # Check and add EditorActionLog fields
        EditorActionLog = apps.get_model('editor_management', 'EditorActionLog')
        log_table_name = EditorActionLog._meta.db_table
        
        cursor.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{log_table_name}'
        """)
        existing_log_columns = {row[0] for row in cursor.fetchall()}
        
        log_fields_to_add = [
            ('action_type', 'varchar(50) NOT NULL DEFAULT \'completed_task\''),
            ('action', 'varchar(255) NOT NULL DEFAULT \'Action performed\''),
            ('related_order_id', 'integer NULL'),
            ('related_task_id', 'integer NULL'),
            ('metadata', 'jsonb NOT NULL DEFAULT \'{}\''),
            ('timestamp', 'timestamp with time zone NOT NULL DEFAULT NOW()'),
        ]
        
        for field_name, field_type in log_fields_to_add:
            if field_name not in existing_log_columns:
                cursor.execute(f"""
                    ALTER TABLE {log_table_name} 
                    ADD COLUMN {field_name} {field_type}
                """)
        
        # Add foreign key constraints if columns were added (check if constraint exists first)
        if 'related_order_id' not in existing_log_columns:
            try:
                cursor.execute(f"""
                    ALTER TABLE {log_table_name}
                    ADD CONSTRAINT {log_table_name}_related_order_id_fkey
                    FOREIGN KEY (related_order_id) REFERENCES orders_order(id)
                    ON DELETE SET NULL
                """)
            except Exception:
                pass  # Constraint might already exist
        
        if 'related_task_id' not in existing_log_columns:
            try:
                cursor.execute(f"""
                    ALTER TABLE {log_table_name}
                    ADD CONSTRAINT {log_table_name}_related_task_id_fkey
                    FOREIGN KEY (related_task_id) REFERENCES editor_management_editortaskassignment(id)
                    ON DELETE SET NULL
                """)
            except Exception:
                pass  # Constraint might already exist


def reverse_add_fields(apps, schema_editor):
    """Reverse migration - remove fields if they exist."""
    # This is a no-op for safety - we don't want to accidentally drop columns
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('editor_management', '0004_add_editor_profile_fields'),
        ('orders', '0002_initial'),
    ]

    operations = [
        # Use SeparateDatabaseAndState to handle database changes separately from state
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(add_fields_if_not_exists, reverse_add_fields),
            ],
            state_operations=[
                # EditorPerformance fields (for Django state tracking only)
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
                # EditorActionLog fields (for Django state tracking only)
                migrations.AddField(
                    model_name='editoractionlog',
                    name='action_type',
                    field=models.CharField(choices=[('claimed_task', 'Claimed Task'), ('started_review', 'Started Review'), ('submitted_review', 'Submitted Review'), ('completed_task', 'Completed Task'), ('rejected_task', 'Rejected Task'), ('unclaimed_task', 'Unclaimed Task')], default='completed_task', help_text='Type of action performed.', max_length=50),
                ),
                migrations.AddField(
                    model_name='editoractionlog',
                    name='action',
                    field=models.CharField(default='Action performed', help_text="Description of the action performed (e.g., 'Reviewed Order').", max_length=255),
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
            ],
        ),
    ]
