# Generated migration for adding can_take_orders flag to WriterProfile

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('writer_management', '0022_alter_writerperformancemetrics_percentile_rank_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='writerprofile',
            name='can_take_orders',
            field=models.BooleanField(
                default=True,
                help_text='If disabled, the writer cannot take orders from their profile, even if their level allows it. Admin can override by assigning orders manually.'
            ),
        ),
    ]

