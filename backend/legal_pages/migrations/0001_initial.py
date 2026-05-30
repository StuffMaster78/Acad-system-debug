import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("websites", "0003_websiteactionlog"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="LegalDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("doc_type", models.CharField(
                    choices=[
                        ("terms_of_service", "Terms of Service"),
                        ("privacy_policy", "Privacy Policy"),
                        ("refund_policy", "Refund Policy"),
                        ("cookie_policy", "Cookie Policy"),
                        ("acceptable_use_policy", "Acceptable Use Policy"),
                        ("writer_agreement", "Writer Agreement"),
                        ("copyright_policy", "Copyright Policy"),
                    ],
                    db_index=True, max_length=64,
                )),
                ("title", models.CharField(max_length=255)),
                ("content", models.TextField(help_text="Full HTML content of the document.")),
                ("version", models.CharField(default="1.0", max_length=20)),
                ("effective_date", models.DateField(default=django.utils.timezone.now)),
                ("is_active", models.BooleanField(db_index=True, default=False)),
                ("requires_re_acceptance", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("website", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="legal_documents",
                    to="websites.website",
                )),
                ("created_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="created_legal_documents",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={"ordering": ["-effective_date", "-created_at"]},
        ),
        migrations.CreateModel(
            name="UserAgreement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("agreed_at", models.DateTimeField(auto_now_add=True)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                ("document", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="user_agreements",
                    to="legal_pages.legaldocument",
                )),
                ("user", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="legal_agreements",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={"ordering": ["-agreed_at"], "unique_together": {("user", "document")}},
        ),
        migrations.CreateModel(
            name="HelpCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=120)),
                ("slug", models.SlugField(max_length=120)),
                ("description", models.TextField(blank=True)),
                ("icon", models.CharField(blank=True, max_length=50)),
                ("audience", models.CharField(
                    choices=[
                        ("all", "All users"), ("client", "Clients"),
                        ("writer", "Writers"), ("staff", "Staff / Support"),
                    ],
                    db_index=True, default="all", max_length=20,
                )),
                ("order", models.PositiveSmallIntegerField(default=0)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("website", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="help_categories",
                    to="websites.website",
                )),
            ],
            options={"ordering": ["order", "title"], "unique_together": {("website", "slug")}},
        ),
        migrations.CreateModel(
            name="HelpArticle",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=255)),
                ("summary", models.CharField(blank=True, max_length=300)),
                ("content", models.TextField(help_text="Full HTML content of the article.")),
                ("audience", models.CharField(
                    choices=[
                        ("all", "All users"), ("client", "Clients"),
                        ("writer", "Writers"), ("staff", "Staff / Support"),
                    ],
                    db_index=True, default="all", max_length=20,
                )),
                ("is_featured", models.BooleanField(default=False)),
                ("is_published", models.BooleanField(db_index=True, default=False)),
                ("order", models.PositiveSmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("category", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="articles",
                    to="legal_pages.helpcategory",
                )),
                ("website", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="help_articles",
                    to="websites.website",
                )),
                ("created_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="created_help_articles",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("updated_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="updated_help_articles",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={"ordering": ["order", "title"], "unique_together": {("website", "slug")}},
        ),
        migrations.AddIndex(
            model_name="legaldocument",
            index=models.Index(fields=["website", "doc_type", "is_active"], name="legal_doc_website_type_active_idx"),
        ),
        migrations.AddIndex(
            model_name="legaldocument",
            index=models.Index(fields=["website", "doc_type", "effective_date"], name="legal_doc_website_type_date_idx"),
        ),
        migrations.AddIndex(
            model_name="useragreement",
            index=models.Index(fields=["user", "agreed_at"], name="legal_agreement_user_date_idx"),
        ),
        migrations.AddIndex(
            model_name="helparticle",
            index=models.Index(fields=["website", "is_published", "audience"], name="help_article_site_pub_aud_idx"),
        ),
        migrations.AddIndex(
            model_name="helparticle",
            index=models.Index(fields=["website", "category", "order"], name="help_article_site_cat_order_idx"),
        ),
    ]
