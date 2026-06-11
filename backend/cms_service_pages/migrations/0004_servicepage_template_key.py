from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cms_service_pages", "0003_servicepage_hero_highlights"),
    ]

    operations = [
        migrations.AddField(
            model_name="servicepage",
            name="template_key",
            field=models.CharField(
                choices=[
                    ("standard_service", "Standard service"),
                    ("essay_service", "Essay / writing service"),
                    ("technical_service", "Technical / data service"),
                    ("healthcare_service", "Healthcare / nursing service"),
                    ("admissions_service", "Admissions service"),
                    ("editing_service", "Editing / proofreading service"),
                    ("online_class_service", "Online class / coursework service"),
                    ("seo_landing_page", "SEO landing page"),
                ],
                default="standard_service",
                help_text=(
                    "Frontend template used by marketing sites such as GradeCrest. "
                    "Controls layout emphasis while this page's copy remains editable."
                ),
                max_length=50,
            ),
        ),
    ]
