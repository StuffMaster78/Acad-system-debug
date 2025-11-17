# Generated manually for new service page models
# Generated on 2024-12-19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service_pages_management', '0003_create_pdf_sample_models'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Create new models
        migrations.CreateModel(
            name='ServicePageCTA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('button_text', models.CharField(max_length=100)),
                ('button_url', models.URLField()),
                ('style', models.CharField(choices=[('primary', 'Primary'), ('secondary', 'Secondary'), ('success', 'Success')], default='primary', max_length=20)),
                ('display_order', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('service_page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ctas', to='service_pages_management.servicepage')),
            ],
            options={
                'ordering': ['display_order'],
            },
        ),
        migrations.CreateModel(
            name='ServicePageEditHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('previous_content', models.TextField()),
                ('current_content', models.TextField()),
                ('changes_summary', models.TextField(blank=True)),
                ('fields_changed', models.JSONField(blank=True, default=list)),
                ('edited_at', models.DateTimeField(auto_now_add=True)),
                ('edited_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('service_page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='edit_history', to='service_pages_management.servicepage')),
            ],
            options={
                'ordering': ['-edited_at'],
            },
        ),
        migrations.CreateModel(
            name='ServicePageFAQ',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=500)),
                ('answer', models.TextField()),
                ('question_slug', models.SlugField(blank=True, max_length=255)),
                ('display_order', models.IntegerField(default=0)),
                ('is_featured', models.BooleanField(default=False)),
                ('upvote_count', models.PositiveIntegerField(default=0)),
                ('accepted_answer', models.BooleanField(default=False)),
                ('service_page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='faqs', to='service_pages_management.servicepage')),
            ],
            options={
                'verbose_name': 'Service Page FAQ',
                'verbose_name_plural': 'Service Page FAQs',
                'ordering': ['is_featured', 'display_order', 'question'],
            },
        ),
        migrations.CreateModel(
            name='ServicePageResource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('url', models.URLField()),
                ('description', models.TextField(blank=True)),
                ('resource_type', models.CharField(choices=[('download', 'Download'), ('link', 'External Link'), ('video', 'Video'), ('document', 'Document')], default='link', max_length=50)),
                ('display_order', models.IntegerField(default=0)),
                ('service_page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resources', to='service_pages_management.servicepage')),
            ],
            options={
                'ordering': ['display_order', 'title'],
            },
        ),
        migrations.CreateModel(
            name='ServicePageSEOMetadata',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keywords', models.CharField(blank=True, help_text='Comma-separated keywords for SEO', max_length=500)),
                ('article_type', models.CharField(choices=[('WebPage', 'WebPage'), ('Service', 'Service'), ('Product', 'Product'), ('LocalBusiness', 'Local Business')], default='WebPage', help_text='Schema.org type', max_length=50)),
                ('og_type', models.CharField(default='website', help_text='Open Graph type', max_length=50)),
                ('og_title', models.CharField(blank=True, help_text='OG title (defaults to page title if empty)', max_length=255)),
                ('og_description', models.TextField(blank=True, help_text='OG description')),
                ('og_image', models.ImageField(blank=True, help_text='OG image (1200x630px recommended)', null=True, upload_to='service_pages/og_images/')),
                ('og_url', models.URLField(blank=True, help_text='Canonical URL for OG')),
                ('og_site_name', models.CharField(blank=True, help_text='Site name for OG', max_length=255)),
                ('twitter_card_type', models.CharField(choices=[('summary', 'Summary'), ('summary_large_image', 'Summary with Large Image'), ('app', 'App'), ('player', 'Player')], default='summary_large_image', max_length=20)),
                ('twitter_title', models.CharField(blank=True, max_length=255)),
                ('twitter_description', models.TextField(blank=True)),
                ('twitter_image', models.ImageField(blank=True, help_text='Twitter image (1200x675px recommended)', null=True, upload_to='service_pages/twitter_images/')),
                ('twitter_site', models.CharField(blank=True, help_text='Twitter handle (e.g., @yourhandle)', max_length=100)),
                ('schema_breadcrumb', models.JSONField(blank=True, default=list, help_text='BreadcrumbList schema data')),
                ('schema_organization', models.JSONField(blank=True, default=dict, help_text='Organization schema data')),
                ('schema_rating', models.JSONField(blank=True, default=dict, help_text='AggregateRating schema (if applicable)')),
                ('google_business_url', models.URLField(blank=True, help_text='Google Business Profile URL')),
                ('canonical_url', models.URLField(blank=True, help_text='Canonical URL for this page')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('service_page', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='seo_metadata', to='service_pages_management.servicepage')),
            ],
            options={
                'verbose_name': 'Service Page SEO Metadata',
                'verbose_name_plural': 'Service Page SEO Metadata',
            },
        ),
        # Rename indexes on existing models
        migrations.RenameIndex(
            model_name='servicepagepdfsample',
            old_name='service_pag_section_idx',
            new_name='service_pag_section_fa0804_idx',
        ),
        migrations.RenameIndex(
            model_name='servicepagepdfsample',
            old_name='service_pag_downloa_idx',
            new_name='service_pag_downloa_dd9ee7_idx',
        ),
        migrations.RenameIndex(
            model_name='servicepagepdfsampledownload',
            old_name='service_pag_pdf_sam_idx',
            new_name='service_pag_pdf_sam_cb0da7_idx',
        ),
        migrations.RenameIndex(
            model_name='servicepagepdfsampledownload',
            old_name='service_pag_user_id_idx',
            new_name='service_pag_user_id_064057_idx',
        ),
        migrations.RenameIndex(
            model_name='servicepagepdfsamplesection',
            old_name='service_pag_service_idx',
            new_name='service_pag_service_cd611e_idx',
        ),
    ]

