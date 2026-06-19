from django.db import migrations


def correct_portal_domains(apps, schema_editor):
    PortalDefinition = apps.get_model("accounts", "PortalDefinition")
    PortalDefinition.objects.filter(code="writer_portal").update(
        name="Writers Creek — Writer Portal",
        domain="app.writerscreek.com",
        is_active=True,
    )
    PortalDefinition.objects.filter(code="internal_admin").update(
        name="Writers Creek — Staff Portal",
        domain="admin.writerscreek.com",
        is_active=True,
    )


def restore_previous_writer_domain(apps, schema_editor):
    PortalDefinition = apps.get_model("accounts", "PortalDefinition")
    PortalDefinition.objects.filter(code="writer_portal").update(
        domain="writerscreek.com",
    )


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0004_portal_definitions_writerscreek"),
    ]

    operations = [
        migrations.RunPython(
            correct_portal_domains,
            reverse_code=restore_previous_writer_domain,
        ),
    ]
