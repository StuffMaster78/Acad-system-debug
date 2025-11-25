# Generated manually
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('writer_management', '0009_add_payment_schedule_preferences'),
        ('websites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # WriterPenNameChangeRequest model
        migrations.CreateModel(
            name='WriterPenNameChangeRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_pen_name', models.CharField(blank=True, help_text='Current pen name (if any)', max_length=100, null=True)),
                ('requested_pen_name', models.CharField(help_text='New pen name requested by the writer', max_length=100)),
                ('reason', models.TextField(help_text='Valid reason for changing the pen name (required)')),
                ('requested_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], db_index=True, default='pending', max_length=20)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('admin_notes', models.TextField(blank=True, help_text='Admin notes on the request', null=True)),
                ('reviewed_by', models.ForeignKey(blank=True, limit_choices_to={'role__in': ['admin', 'superadmin']}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pen_name_reviews', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pen_name_change_requests', to='websites.website')),
                ('writer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pen_name_change_requests', to='writer_management.writerprofile')),
            ],
            options={
                'ordering': ['-requested_at'],
            },
        ),
        migrations.AddIndex(
            model_name='writerpennamechangerequest',
            index=models.Index(fields=['status', 'requested_at'], name='writer_mana_status_7a8f2d_idx'),
        ),
        migrations.AddIndex(
            model_name='writerpennamechangerequest',
            index=models.Index(fields=['writer', 'status'], name='writer_mana_writer__8c9e3f_idx'),
        ),
        # WriterResourceCategory model
        migrations.CreateModel(
            name='WriterResourceCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="Category name (e.g., 'Writing Tips', 'Style Guides')", max_length=100)),
                ('description', models.TextField(blank=True, help_text='Brief description of the category', null=True)),
                ('display_order', models.PositiveIntegerField(default=0, help_text='Order in which categories are displayed')),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='writer_resource_categories', to='websites.website')),
            ],
            options={
                'verbose_name_plural': 'Writer Resource Categories',
                'ordering': ['display_order', 'name'],
                'unique_together': {('website', 'name')},
            },
        ),
        # WriterResource model
        migrations.CreateModel(
            name='WriterResource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Resource title', max_length=255)),
                ('description', models.TextField(blank=True, help_text='Description of the resource', null=True)),
                ('resource_type', models.CharField(choices=[('document', 'Document (PDF, DOC, etc.)'), ('link', 'External Link'), ('video', 'Video'), ('article', 'Article/Guide'), ('tool', 'Tool/Software')], default='document', max_length=20)),
                ('file', models.FileField(blank=True, help_text='Upload a document (PDF, DOC, etc.)', null=True, upload_to='writer_resources/')),
                ('external_url', models.URLField(blank=True, help_text='External link URL', null=True)),
                ('video_url', models.URLField(blank=True, help_text='Video URL (YouTube, Vimeo, etc.)', null=True)),
                ('content', models.TextField(blank=True, help_text='Article/guide content (HTML supported)', null=True)),
                ('is_featured', models.BooleanField(db_index=True, default=False, help_text='Feature this resource prominently')),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('display_order', models.PositiveIntegerField(default=0, help_text='Order in which resources are displayed')),
                ('view_count', models.PositiveIntegerField(default=0, help_text='Number of times this resource has been viewed')),
                ('download_count', models.PositiveIntegerField(default=0, help_text='Number of times this resource has been downloaded')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resources', to='writer_management.writerresourcecategory')),
                ('created_by', models.ForeignKey(limit_choices_to={'role__in': ['admin', 'superadmin']}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_writer_resources', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, limit_choices_to={'role__in': ['admin', 'superadmin']}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_writer_resources', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='writer_resources', to='websites.website')),
            ],
            options={
                'ordering': ['display_order', '-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='writerresource',
            index=models.Index(fields=['website', 'is_active', 'is_featured'], name='writer_mana_website_9c8e4f_idx'),
        ),
        migrations.AddIndex(
            model_name='writerresource',
            index=models.Index(fields=['category', 'is_active'], name='writer_mana_categor_7d9e2f_idx'),
        ),
        # WriterResourceView model
        migrations.CreateModel(
            name='WriterResourceView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('viewed_at', models.DateTimeField(auto_now_add=True)),
                ('resource', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='views', to='writer_management.writerresource')),
                ('writer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resource_views', to='writer_management.writerprofile')),
            ],
            options={
                'unique_together': {('resource', 'writer')},
            },
        ),
        migrations.AddIndex(
            model_name='writerresourceview',
            index=models.Index(fields=['writer', 'viewed_at'], name='writer_mana_writer__a9e3f1_idx'),
        ),
    ]

