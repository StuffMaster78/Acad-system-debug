# Generated migration to make OrderFileCategory.website nullable for universal categories

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order_files', '0006_rename_order_files_order_i_uploaded_idx_order_files_order_i_58c45b_idx_and_more'),
    ]

    operations = [
        # Remove the unique constraint on name first
        migrations.AlterField(
            model_name='orderfilecategory',
            name='name',
            field=models.CharField(max_length=100),
        ),
        # Make website nullable
        migrations.AlterField(
            model_name='orderfilecategory',
            name='website',
            field=models.ForeignKey(
                blank=True,
                help_text='Leave blank for universal categories (available to all websites), or select a website for website-specific categories',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='order_file_category',
                to='websites.website'
            ),
        ),
        # Add unique_together constraint for name + website
        migrations.AlterUniqueTogether(
            name='orderfilecategory',
            unique_together={('name', 'website')},
        ),
    ]

