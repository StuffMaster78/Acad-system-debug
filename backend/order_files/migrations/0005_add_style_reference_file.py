# Generated migration for StyleReferenceFile model

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_files', '0004_enhance_file_versioning'),
        ('orders', '0013_add_writer_acknowledgment_message_review_reminders'),
        ('websites', '0006_enhance_file_versioning'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StyleReferenceFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(help_text='The style reference file (PDF, DOCX, etc.)', upload_to='style_references/')),
                ('reference_type', models.CharField(choices=[('previous_paper', 'Previous Paper'), ('instructor_feedback', 'Instructor Feedback'), ('style_guide', 'Style Guide'), ('sample_work', 'Sample Work')], default='previous_paper', help_text='Type of style reference (previous paper, instructor feedback, etc.)', max_length=50)),
                ('description', models.TextField(blank=True, help_text='Optional description or notes about this style reference', null=True)),
                ('file_name', models.CharField(help_text='Original filename', max_length=255)),
                ('file_size', models.PositiveIntegerField(blank=True, help_text='File size in bytes', null=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, help_text='When the style reference was uploaded')),
                ('is_visible_to_writer', models.BooleanField(default=True, help_text='Whether the writer can view this style reference')),
                ('order', models.ForeignKey(help_text='The order this style reference is associated with', on_delete=django.db.models.deletion.CASCADE, related_name='style_reference_files', to='orders.order')),
                ('uploaded_by', models.ForeignKey(help_text='Client who uploaded this style reference', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_style_references', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='style_reference_files', to='websites.website')),
            ],
            options={
                'verbose_name': 'Style Reference File',
                'verbose_name_plural': 'Style Reference Files',
                'ordering': ['-uploaded_at'],
            },
        ),
        migrations.AddIndex(
            model_name='stylereferencefile',
            index=models.Index(fields=['order', 'uploaded_at'], name='order_files_order_i_uploaded_idx'),
        ),
        migrations.AddIndex(
            model_name='stylereferencefile',
            index=models.Index(fields=['order', 'reference_type'], name='order_files_order_i_ref_type_idx'),
        ),
    ]

