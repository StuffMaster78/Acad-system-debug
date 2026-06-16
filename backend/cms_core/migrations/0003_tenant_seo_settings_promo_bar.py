from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cms_core", "0002_tenant_seo_settings_branding"),
    ]

    operations = [
        migrations.AddField(
            model_name="tenantseosettings",
            name="promo_bar_enabled",
            field=models.BooleanField(
                default=True,
                help_text="Show the announcement bar at the top of every page.",
            ),
        ),
        migrations.AddField(
            model_name="tenantseosettings",
            name="promo_code",
            field=models.CharField(
                blank=True,
                max_length=50,
                help_text="Promo code displayed in the bar (e.g. GRADE15).",
            ),
        ),
        migrations.AddField(
            model_name="tenantseosettings",
            name="promo_message",
            field=models.CharField(
                blank=True,
                max_length=200,
                help_text="Text shown before the code (e.g. 'First order? Use code').",
            ),
        ),
        migrations.AddField(
            model_name="tenantseosettings",
            name="promo_suffix",
            field=models.CharField(
                blank=True,
                max_length=200,
                help_text="Text shown after the code (e.g. 'for 15% off · Free plagiarism report').",
            ),
        ),
    ]
