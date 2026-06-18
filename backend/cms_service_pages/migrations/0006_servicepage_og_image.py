from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("cms_service_pages", "0005_add_dispute_writer_response_support_management_and_orders"),
        ("wagtailimages", "0026_delete_uploadedimage"),
    ]

    operations = [
        migrations.AddField(
            model_name="servicepage",
            name="og_image",
            field=models.ForeignKey(
                blank=True,
                help_text="Social-sharing image for this service page. Overrides the tenant-level default OG image.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
    ]
