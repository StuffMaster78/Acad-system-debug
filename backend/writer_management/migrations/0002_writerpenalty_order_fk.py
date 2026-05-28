import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('writer_management', '0001_initial'),
        ('orders', '0004_rename_orders_orde_order_i_idx_orders_orde_order_i_d0cfbe_idx'),
    ]

    operations = [
        migrations.AddField(
            model_name='writerpenalty',
            name='order',
            field=models.ForeignKey(
                blank=True,
                help_text='The order this penalty relates to.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='writer_penalties',
                to='orders.order',
            ),
        ),
    ]
