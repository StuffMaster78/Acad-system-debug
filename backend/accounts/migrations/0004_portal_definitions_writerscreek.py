from __future__ import annotations

from django.db import migrations


PORTALS = [
    {
        "code": "writer_portal",
        "name": "Writers Creek — Writer Portal",
        "domain": "writerscreek.com",
    },
    {
        "code": "internal_admin",
        "name": "Writers Creek — Staff Portal",
        "domain": "admin.writerscreek.com",
    },
]


def create_portals(apps, schema_editor):
    PortalDefinition = apps.get_model("accounts", "PortalDefinition")
    for data in PORTALS:
        PortalDefinition.objects.update_or_create(
            code=data["code"],
            defaults={"name": data["name"], "domain": data["domain"], "is_active": True},
        )


def delete_portals(apps, schema_editor):
    PortalDefinition = apps.get_model("accounts", "PortalDefinition")
    PortalDefinition.objects.filter(code__in=[p["code"] for p in PORTALS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_user_acquisition"),
    ]

    operations = [
        migrations.RunPython(create_portals, reverse_code=delete_portals),
    ]
