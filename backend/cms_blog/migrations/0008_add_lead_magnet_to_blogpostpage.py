from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("cms_attachments", "0001_initial"),
        ("cms_blog", "0007_alter_blogpostpage_body"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogpostpage",
            name="lead_magnet",
            field=models.ForeignKey(
                blank=True,
                help_text=(
                    "Optional: attach a gated resource (cheat sheet, template, guide) "
                    "that appears after the article body. Leave blank to show no download offer."
                ),
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="blog_posts",
                to="cms_attachments.attachment",
            ),
        ),
    ]
