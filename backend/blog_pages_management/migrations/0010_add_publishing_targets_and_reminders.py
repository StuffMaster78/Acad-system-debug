# Generated manually for publishing targets and content freshness reminders

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_pages_management', '0009_add_editor_tracking_and_collaboration'),
        ('websites', '0008_set_guest_checkout_safe_defaults'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Create WebsitePublishingTarget model
        migrations.CreateModel(
            name='WebsitePublishingTarget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monthly_target', models.PositiveIntegerField(default=4, help_text='Target number of blog posts to publish per month')),
                ('is_auto_estimated', models.BooleanField(default=True, help_text='Whether target was auto-estimated or manually set by admin')),
                ('estimation_reason', models.TextField(blank=True, help_text='Reason for the estimated target (e.g., \'Based on industry average\')')),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('freshness_threshold_months', models.PositiveIntegerField(default=3, help_text='Number of months before content is considered stale')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_publishing_targets', to=settings.AUTH_USER_MODEL)),
                ('website', models.OneToOneField(help_text='Website this target applies to', on_delete=django.db.models.deletion.CASCADE, related_name='publishing_target', to='websites.website')),
            ],
            options={
                'verbose_name': 'Website Publishing Target',
                'verbose_name_plural': 'Website Publishing Targets',
            },
        ),
        
        # Create CategoryPublishingTarget model
        migrations.CreateModel(
            name='CategoryPublishingTarget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monthly_target', models.PositiveIntegerField(default=1, help_text='Target number of posts in this category per month')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this target is active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(help_text='Category this target applies to', on_delete=django.db.models.deletion.CASCADE, related_name='publishing_targets', to='blog_pages_management.blogcategory')),
                ('website', models.ForeignKey(help_text='Website this target applies to', on_delete=django.db.models.deletion.CASCADE, related_name='category_publishing_targets', to='websites.website')),
            ],
            options={
                'verbose_name': 'Category Publishing Target',
                'verbose_name_plural': 'Category Publishing Targets',
                'unique_together': {('website', 'category')},
            },
        ),
        
        # Create ContentFreshnessReminder model
        migrations.CreateModel(
            name='ContentFreshnessReminder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_reminder_sent', models.DateTimeField(blank=True, null=True)),
                ('reminder_count', models.PositiveIntegerField(default=0)),
                ('is_acknowledged', models.BooleanField(default=False)),
                ('acknowledged_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('acknowledged_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='acknowledged_freshness_reminders', to=settings.AUTH_USER_MODEL)),
                ('blog_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='freshness_reminders', to='blog_pages_management.blogpost')),
            ],
            options={
                'verbose_name': 'Content Freshness Reminder',
                'verbose_name_plural': 'Content Freshness Reminders',
            },
        ),
        migrations.AddIndex(
            model_name='contentfreshnessreminder',
            index=models.Index(fields=['blog_post', 'is_acknowledged'], name='blog_pages__blog_post_ack_idx'),
        ),
    ]

