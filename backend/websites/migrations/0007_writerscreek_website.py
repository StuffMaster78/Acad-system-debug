from __future__ import annotations

from django.db import migrations


def create_website(apps, schema_editor):
    Website = apps.get_model("websites", "Website")
    Website.objects.update_or_create(
        domain="writerscreek.com",
        defaults={
            "name": "Writers Creek",
            "slug": "writerscreek",
            "is_active": True,
            "is_deleted": False,
        },
    )


def delete_website(apps, schema_editor):
    Website = apps.get_model("websites", "Website")
    Website.objects.filter(domain="writerscreek.com").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("websites", "0006_add_social_links_to_website_branding"),
    ]

    operations = [
        migrations.RunPython(create_website, reverse_code=delete_website),
    ]
