# Generated manually to fix base_amount field type
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fines', '0004_merge_20251104_0753'),
    ]

    operations = [
        # Change base_amount from DecimalField to CharField
        migrations.AlterField(
            model_name='finetypeconfig',
            name='base_amount',
            field=models.CharField(
                blank=True,
                choices=[('writer_compensation', 'Writer Compensation'), ('total_price', 'Order Total Price')],
                default='writer_compensation',
                help_text='Base amount for percentage calculation',
                max_length=20,
                null=True
            ),
        ),
        # Fix is_system_defined choices to match model
        migrations.AlterField(
            model_name='finetypeconfig',
            name='is_system_defined',
            field=models.CharField(
                choices=[('system', 'System-Defined (Late Submission)'), ('admin', 'Admin-Defined')],
                default='admin',
                help_text='System-defined types (e.g., late submission) cannot be deleted',
                max_length=10
            ),
        ),
    ]

