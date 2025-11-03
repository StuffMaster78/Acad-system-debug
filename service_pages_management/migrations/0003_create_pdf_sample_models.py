# Generated migration for ServicePage PDF Sample models
from django.conf import settings
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_pages_management', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ServicePagePDFSampleSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text="Section title (e.g., 'Download Samples', 'Resources')", max_length=255)),
                ('description', models.TextField(blank=True, help_text='Description of what these samples contain')),
                ('display_order', models.IntegerField(default=0, help_text='Order for displaying sections within the service page')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this section is visible')),
                ('requires_auth', models.BooleanField(default=False, help_text='Require user authentication to download')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('service_page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pdf_sample_sections', to='service_pages_management.servicepage')),
            ],
            options={
                'verbose_name': 'Service Page PDF Sample Section',
                'verbose_name_plural': 'Service Page PDF Sample Sections',
                'ordering': ['display_order', 'title'],
            },
        ),
        migrations.CreateModel(
            name='ServicePagePDFSample',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Display name for this PDF', max_length=255)),
                ('description', models.TextField(blank=True, help_text='Brief description of what this PDF contains')),
                ('pdf_file', models.FileField(help_text='PDF file to upload (max 10MB)', upload_to='service_pages_pdf_samples/%Y/%m/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])])),
                ('file_size', models.PositiveIntegerField(blank=True, help_text='File size in bytes (auto-calculated)', null=True)),
                ('display_order', models.IntegerField(default=0, help_text='Order for displaying PDFs within the section')),
                ('download_count', models.PositiveIntegerField(default=0, help_text='Number of times this PDF has been downloaded')),
                ('is_featured', models.BooleanField(default=False, help_text='Featured PDFs appear first')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this PDF is available for download')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pdf_samples', to='service_pages_management.servicepagepdfsamplesection')),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_service_pdf_samples', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Service Page PDF Sample',
                'verbose_name_plural': 'Service Page PDF Samples',
                'ordering': ['is_featured', 'display_order', 'title'],
            },
        ),
        migrations.CreateModel(
            name='ServicePagePDFSampleDownload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('session_id', models.CharField(blank=True, max_length=255)),
                ('downloaded_at', models.DateTimeField(auto_now_add=True)),
                ('pdf_sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='downloads', to='service_pages_management.servicepagepdfsample')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='service_pdf_downloads', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Service Page PDF Sample Download',
                'verbose_name_plural': 'Service Page PDF Sample Downloads',
                'ordering': ['-downloaded_at'],
            },
        ),
        migrations.AddIndex(
            model_name='servicepagepdfsamplesection',
            index=models.Index(fields=['service_page', 'is_active'], name='service_pag_service_idx'),
        ),
        migrations.AddIndex(
            model_name='servicepagepdfsample',
            index=models.Index(fields=['section', 'is_active'], name='service_pag_section_idx'),
        ),
        migrations.AddIndex(
            model_name='servicepagepdfsample',
            index=models.Index(fields=['download_count'], name='service_pag_downloa_idx'),
        ),
        migrations.AddIndex(
            model_name='servicepagepdfsampledownload',
            index=models.Index(fields=['pdf_sample', 'downloaded_at'], name='service_pag_pdf_sam_idx'),
        ),
        migrations.AddIndex(
            model_name='servicepagepdfsampledownload',
            index=models.Index(fields=['user', 'downloaded_at'], name='service_pag_user_id_idx'),
        ),
    ]

