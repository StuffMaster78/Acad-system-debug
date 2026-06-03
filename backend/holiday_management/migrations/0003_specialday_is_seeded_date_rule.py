from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("holiday_management", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="specialday",
            name="is_seeded",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Pre-seeded system holiday. Admins may only edit discount/reminder "
                    "settings — name, date, and type are locked."
                ),
            ),
        ),
        migrations.AddField(
            model_name="specialday",
            name="date_rule",
            field=models.JSONField(
                blank=True,
                null=True,
                help_text=(
                    "Rule for floating annual dates. "
                    "nth_weekday: {type, month, n, weekday, offset_days?} "
                    "last_weekday: {type, month, weekday} "
                    "easter: {type, offset_days?}"
                ),
            ),
        ),
    ]
