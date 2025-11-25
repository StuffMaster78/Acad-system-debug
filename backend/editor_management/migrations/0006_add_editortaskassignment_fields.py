# Generated migration for EditorTaskAssignment missing fields
from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


def add_editortaskassignment_fields_if_not_exists(apps, schema_editor):
    """Add fields only if they don't already exist in the database."""
    EditorTaskAssignment = apps.get_model('editor_management', 'EditorTaskAssignment')
    table_name = EditorTaskAssignment._meta.db_table
    
    with schema_editor.connection.cursor() as cursor:
        # Get existing columns
        cursor.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
        """)
        existing_columns = {row[0] for row in cursor.fetchall()}
        
        # Fields to add
        fields_to_add = [
            ('assignment_type', 'varchar(20) NOT NULL DEFAULT \'auto\''),
            ('assigned_by_id', 'integer NULL'),
            ('assigned_at', 'timestamp with time zone NOT NULL DEFAULT NOW()'),
            ('review_status', 'varchar(20) NOT NULL DEFAULT \'pending\''),
            ('started_at', 'timestamp with time zone NULL'),
            ('reviewed_at', 'timestamp with time zone NULL'),
            ('notes', 'text NULL'),
            ('editor_rating', 'integer NULL'),
        ]
        
        for field_name, field_type in fields_to_add:
            if field_name not in existing_columns:
                cursor.execute(f"""
                    ALTER TABLE {table_name} 
                    ADD COLUMN {field_name} {field_type}
                """)
        
        # Add foreign key constraint if column was added
        if 'assigned_by_id' not in existing_columns:
            try:
                # Get the user model table name
                User = apps.get_model(settings.AUTH_USER_MODEL)
                user_table = User._meta.db_table
                cursor.execute(f"""
                    ALTER TABLE {table_name}
                    ADD CONSTRAINT {table_name}_assigned_by_id_fkey
                    FOREIGN KEY (assigned_by_id) REFERENCES {user_table}(id)
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
        ('editor_management', '0005_add_all_missing_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(add_editortaskassignment_fields_if_not_exists, reverse_add_fields),
            ],
            state_operations=[
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
            ],
        ),
    ]
