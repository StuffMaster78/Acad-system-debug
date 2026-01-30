from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("communications", "0011_add_communication_thread_indexes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="communicationlog",
            name="order",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.CASCADE,
                related_name="message_logs",
                to="orders.order",
            ),
        ),
    ]
