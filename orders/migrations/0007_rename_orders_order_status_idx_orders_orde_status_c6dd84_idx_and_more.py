# Generated manually for index renames and writerprogress changes
# Generated on 2024-12-19

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_add_order_indexes'),
    ]

    operations = [
        # Rename indexes to match Django's auto-generated naming convention
        migrations.RenameIndex(
            model_name='order',
            old_name='orders_order_status_idx',
            new_name='orders_orde_status_c6dd84_idx',
        ),
        migrations.RenameIndex(
            model_name='order',
            old_name='orders_order_is_paid_idx',
            new_name='orders_orde_is_paid_921844_idx',
        ),
        migrations.RenameIndex(
            model_name='order',
            old_name='orders_order_created_at_idx',
            new_name='orders_orde_created_0e92de_idx',
        ),
        migrations.RenameIndex(
            model_name='order',
            old_name='orders_order_client_idx',
            new_name='orders_orde_client__7a26db_idx',
        ),
        migrations.RenameIndex(
            model_name='order',
            old_name='orders_order_assigned_writer_idx',
            new_name='orders_orde_assigne_07d83e_idx',
        ),
        migrations.RenameIndex(
            model_name='order',
            old_name='orders_order_website_idx',
            new_name='orders_orde_website_c68832_idx',
        ),
        migrations.RenameIndex(
            model_name='order',
            old_name='orders_order_status_paid_idx',
            new_name='orders_orde_status_93a2c3_idx',
        ),
        migrations.RenameIndex(
            model_name='order',
            old_name='orders_order_client_status_idx',
            new_name='orders_orde_client__7fa500_idx',
        ),
        migrations.RenameIndex(
            model_name='order',
            old_name='orders_order_writer_status_idx',
            new_name='orders_orde_assigne_fe4cb5_idx',
        ),
        migrations.RenameIndex(
            model_name='order',
            old_name='orders_order_website_status_idx',
            new_name='orders_orde_website_e58188_idx',
        ),
        migrations.RenameIndex(
            model_name='order',
            old_name='orders_order_status_created_idx',
            new_name='orders_orde_status_25e057_idx',
        ),
        migrations.RenameIndex(
            model_name='order',
            old_name='orders_order_paid_created_idx',
            new_name='orders_orde_is_paid_304842_idx',
        ),
        # Rename indexes on writerprogress
        migrations.RenameIndex(
            model_name='writerprogress',
            old_name='orders_writ_order_i_idx',
            new_name='orders_writ_order_i_0ec762_idx',
        ),
        migrations.RenameIndex(
            model_name='writerprogress',
            old_name='orders_writ_writer_idx',
            new_name='orders_writ_writer__70d8cf_idx',
        ),
        migrations.RenameIndex(
            model_name='writerprogress',
            old_name='orders_writ_is_with_idx',
            new_name='orders_writ_is_with_8460ec_idx',
        ),
        # Alter unique_together for writerprogress (remove it)
        migrations.AlterUniqueTogether(
            name='writerprogress',
            unique_together=set(),
        ),
        # Alter fields on writerprogress
        migrations.AlterField(
            model_name='writerprogress',
            name='notes',
            field=models.TextField(blank=True, help_text='Optional notes about the progress update.', null=True),
        ),
        migrations.AlterField(
            model_name='writerprogress',
            name='progress_percentage',
            field=models.PositiveIntegerField(help_text='Percentage of work completed (0-100).', validators=[django.core.validators.MaxValueValidator(100)]),
        ),
    ]

