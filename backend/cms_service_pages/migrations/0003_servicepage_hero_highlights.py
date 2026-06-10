import django.db.models.deletion
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cms_service_pages", "0002_alter_servicepage_body"),
    ]

    operations = [
        migrations.AddField(
            model_name="servicepage",
            name="hero_headline",
            field=models.CharField(
                blank=True,
                help_text="Override the hero headline. Leave blank to use the static default.",
                max_length=200,
            ),
        ),
        migrations.AddField(
            model_name="servicepage",
            name="hero_sub",
            field=models.CharField(
                blank=True,
                help_text="Override the hero sub-headline. Leave blank to use the static default.",
                max_length=500,
            ),
        ),
        migrations.AddField(
            model_name="servicepage",
            name="includes_items",
            field=wagtail.fields.StreamField(
                [("item", 0)],
                blank=True,
                block_lookup={0: ("wagtail.blocks.CharBlock", (), {"label": "Item", "max_length": 300})},
                use_json_field=True,
                verbose_name="What's included",
            ),
        ),
        migrations.AddField(
            model_name="servicepage",
            name="delivers_items",
            field=wagtail.fields.StreamField(
                [("item", 0)],
                blank=True,
                block_lookup={0: ("wagtail.blocks.CharBlock", (), {"label": "Item", "max_length": 300})},
                use_json_field=True,
                verbose_name="What you receive",
            ),
        ),
        migrations.AddField(
            model_name="servicepage",
            name="who_for",
            field=models.TextField(
                blank=True,
                verbose_name="Who this is for",
            ),
        ),
    ]
