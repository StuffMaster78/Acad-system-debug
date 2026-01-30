from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("special_orders", "0005_merge_20260106_1150"),
    ]

    operations = [
        migrations.AddField(
            model_name="specialorder",
            name="budget",
            field=models.DecimalField(
                blank=True,
                null=True,
                max_digits=10,
                decimal_places=2,
                help_text="Client's stated budget for negotiation purposes",
            ),
        ),
    ]
