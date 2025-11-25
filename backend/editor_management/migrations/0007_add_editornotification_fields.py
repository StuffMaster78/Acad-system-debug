# Generated migration for EditorNotification missing fields
import django.db.models.deletion
from django.db import migrations, models


def add_editornotification_fields_if_not_exists(apps, schema_editor):
    """Add fields only if they don't already exist in the database."""
    EditorNotification = apps.get_model('editor_management', 'EditorNotification')
    table_name = EditorNotification._meta.db_table
    
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
            ('related_order_id', 'integer NULL'),
            ('related_task_id', 'integer NULL'),
            ('notification_type', 'varchar(50) NOT NULL DEFAULT \'info\''),
        ]
        
        for field_name, field_type in fields_to_add:
            if field_name not in existing_columns:
                cursor.execute(f"""
                    ALTER TABLE {table_name} 
                    ADD COLUMN {field_name} {field_type}
                """)
        
        # Add foreign key constraints if columns were added
        if 'related_order_id' not in existing_columns:
            try:
                cursor.execute(f"""
                    ALTER TABLE {table_name}
                    ADD CONSTRAINT {table_name}_related_order_id_fkey
                    FOREIGN KEY (related_order_id) REFERENCES orders_order(id)
                    ON DELETE SET NULL
                """)
            except Exception:
                pass  # Constraint might already exist
        
        if 'related_task_id' not in existing_columns:
            try:
                cursor.execute(f"""
                    ALTER TABLE {table_name}
                    ADD CONSTRAINT {table_name}_related_task_id_fkey
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
        ('editor_management', '0006_add_editortaskassignment_fields'),
        ('orders', '0002_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(add_editornotification_fields_if_not_exists, reverse_add_fields),
            ],
            state_operations=[
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
            ],
        ),
    ]
