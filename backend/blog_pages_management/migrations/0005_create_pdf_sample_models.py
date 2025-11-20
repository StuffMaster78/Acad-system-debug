# Generated migration for creating PDF sample models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog_pages_management', '0004_add_blogpost_content_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='PDFSampleSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text="Section title (e.g., 'Download Sample', 'Case Studies')", max_length=255)),
                ('description', models.TextField(blank=True, help_text='Description of what these samples contain')),
                ('display_order', models.IntegerField(default=0, help_text='Order for displaying sections within the blog')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this section is visible')),
                ('requires_auth', models.BooleanField(default=False, help_text='Require user authentication to download')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('blog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pdf_sample_sections', to='blog_pages_management.blogpost')),
            ],
            options={
                'verbose_name': 'PDF Sample Section',
                'verbose_name_plural': 'PDF Sample Sections',
                'ordering': ['display_order', 'title'],
            },
        ),
        migrations.CreateModel(
            name='PDFSample',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text="Display name for this PDF (e.g., 'Sample Report 2024')", max_length=255)),
                ('description', models.TextField(blank=True, help_text='Brief description of what this PDF contains')),
                ('pdf_file', models.FileField(help_text='PDF file to upload (max 10MB)', upload_to='blog_pdf_samples/%Y/%m/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])])),
                ('file_size', models.PositiveIntegerField(blank=True, help_text='File size in bytes (auto-calculated)', null=True)),
                ('display_order', models.IntegerField(default=0, help_text='Order for displaying PDFs within the section')),
                ('download_count', models.PositiveIntegerField(default=0, help_text='Number of times this PDF has been downloaded')),
                ('is_featured', models.BooleanField(default=False, help_text='Featured PDFs appear first')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this PDF is available for download')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pdf_samples', to='blog_pages_management.pdfsamplesection')),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_pdf_samples', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'PDF Sample',
                'verbose_name_plural': 'PDF Samples',
                'ordering': ['is_featured', 'display_order', 'title'],
            },
        ),
        migrations.CreateModel(
            name='PDFSampleDownload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(blank=True, help_text='IP address of the downloader', null=True)),
                ('user_agent', models.TextField(blank=True, help_text='Browser user agent')),
                ('session_id', models.CharField(blank=True, help_text='Session ID for tracking', max_length=255)),
                ('downloaded_at', models.DateTimeField(auto_now_add=True)),
                ('pdf_sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='downloads', to='blog_pages_management.pdfsample')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pdf_downloads', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'PDF Sample Download',
                'verbose_name_plural': 'PDF Sample Downloads',
                'ordering': ['-downloaded_at'],
            },
        ),
        migrations.AddIndex(
            model_name='pdfsamplesection',
            index=models.Index(fields=['blog', 'is_active'], name='blog_pages__blog_id_abc123_idx'),
        ),
        migrations.AddIndex(
            model_name='pdfsample',
            index=models.Index(fields=['section', 'is_active'], name='blog_pages__section_xyz789_idx'),
        ),
        migrations.AddIndex(
            model_name='pdfsample',
            index=models.Index(fields=['download_count'], name='blog_pages__downloa_def456_idx'),
        ),
        migrations.AddIndex(
            model_name='pdfsampledownload',
            index=models.Index(fields=['pdf_sample', 'downloaded_at'], name='blog_pages__pdf_sam_ghi012_idx'),
        ),
        migrations.AddIndex(
            model_name='pdfsampledownload',
            index=models.Index(fields=['user', 'downloaded_at'], name='blog_pages__user_id_jkl345_idx'),
        ),
    ]

