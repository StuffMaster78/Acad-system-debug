# Generated migration for profile changes and privacy settings

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_add_security_features'),
        ('websites', '0006_enhance_file_versioning'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Profile Change Requests
        migrations.CreateModel(
            name='ProfileChangeRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('change_type', models.CharField(choices=[('bio', 'Bio'), ('avatar', 'Avatar'), ('pen_name', 'Pen Name'), ('other', 'Other')], help_text='Type of profile change', max_length=50)),
                ('current_value', models.TextField(blank=True, help_text='Current value of the field being changed')),
                ('requested_value', models.TextField(help_text='Requested new value')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled')], default='pending', help_text='Current status of the request', max_length=20)),
                ('approved_at', models.DateTimeField(blank=True, help_text='When the request was approved/rejected', null=True)),
                ('rejection_reason', models.TextField(blank=True, help_text='Reason for rejection if rejected')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='When the request was created')),
                ('completed_at', models.DateTimeField(blank=True, help_text='When the change was completed', null=True)),
                ('approved_by', models.ForeignKey(blank=True, help_text='Admin who approved/rejected the change', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_profile_changes', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(help_text='User requesting profile change', on_delete=django.db.models.deletion.CASCADE, related_name='profile_change_requests', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(help_text='Website context', on_delete=django.db.models.deletion.CASCADE, related_name='profile_change_requests', to='websites.website')),
            ],
            options={
                'verbose_name': 'Profile Change Request',
                'verbose_name_plural': 'Profile Change Requests',
                'ordering': ['-created_at'],
            },
        ),
        # Writer Avatar Uploads
        migrations.CreateModel(
            name='WriterAvatarUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar_file', models.ImageField(help_text='Uploaded avatar file', upload_to='writer_avatars/pending/')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', help_text='Approval status', max_length=20)),
                ('approved_at', models.DateTimeField(blank=True, help_text='When approved/rejected', null=True)),
                ('rejection_reason', models.TextField(blank=True, help_text='Reason for rejection')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('approved_by', models.ForeignKey(blank=True, help_text='Admin who approved/rejected', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_avatars', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(help_text='Writer uploading the avatar', on_delete=django.db.models.deletion.CASCADE, related_name='avatar_uploads', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(help_text='Website context', on_delete=django.db.models.deletion.CASCADE, related_name='avatar_uploads', to='websites.website')),
            ],
            options={
                'verbose_name': 'Writer Avatar Upload',
                'verbose_name_plural': 'Writer Avatar Uploads',
                'ordering': ['-created_at'],
            },
        ),
        # Privacy Settings
        migrations.CreateModel(
            name='WriterPrivacySettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('show_writer_id', models.BooleanField(default=True, help_text='Clients see Writer ID')),
                ('show_pen_name', models.BooleanField(default=True, help_text='Clients see Pen Name (if set)')),
                ('show_completed_orders_count', models.BooleanField(default=True, help_text='Clients see number of completed orders')),
                ('show_rating', models.BooleanField(default=True, help_text='Clients see writer rating')),
                ('show_workload', models.BooleanField(default=True, help_text='Clients see current workload')),
                ('show_bio', models.BooleanField(default=False, help_text='Clients see bio (admin-controlled)')),
                ('show_avatar', models.BooleanField(default=True, help_text='Clients see avatar (if approved)')),
                ('bio_approved', models.BooleanField(default=False, help_text='Whether bio is approved by admin')),
                ('bio_approved_at', models.DateTimeField(blank=True, help_text='When bio was approved', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('bio_approved_by', models.ForeignKey(blank=True, help_text='Admin who approved the bio', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_bios', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(help_text='Writer whose privacy settings are configured', on_delete=django.db.models.deletion.CASCADE, related_name='writer_privacy_settings', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(help_text='Website context', on_delete=django.db.models.deletion.CASCADE, related_name='writer_privacy_settings', to='websites.website')),
            ],
            options={
                'verbose_name': 'Writer Privacy Settings',
                'verbose_name_plural': 'Writer Privacy Settings',
            },
        ),
        migrations.CreateModel(
            name='ClientPrivacySettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('show_client_id', models.BooleanField(default=True, help_text='Writers see Client ID')),
                ('show_pen_name', models.BooleanField(default=True, help_text='Writers see Pen Name (if set)')),
                ('show_real_name', models.BooleanField(default=False, help_text='Writers see real name (admin-controlled)')),
                ('show_email', models.BooleanField(default=False, help_text='Writers see email (admin-controlled)')),
                ('show_avatar', models.BooleanField(default=True, help_text='Writers see avatar')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(help_text='Client whose privacy settings are configured', on_delete=django.db.models.deletion.CASCADE, related_name='client_privacy_settings', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(help_text='Website context', on_delete=django.db.models.deletion.CASCADE, related_name='client_privacy_settings', to='websites.website')),
            ],
            options={
                'verbose_name': 'Client Privacy Settings',
                'verbose_name_plural': 'Client Privacy Settings',
            },
        ),
        migrations.CreateModel(
            name='PenName',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pen_name', models.CharField(help_text='The pen name', max_length=100)),
                ('is_active', models.BooleanField(default=True, help_text='Whether this is the active pen name')),
                ('is_approved', models.BooleanField(default=False, help_text='Whether pen name is approved by admin (for writers)')),
                ('approved_at', models.DateTimeField(blank=True, help_text='When pen name was approved', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('approved_by', models.ForeignKey(blank=True, help_text='Admin who approved the pen name', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_pen_names', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(help_text='User who owns this pen name', on_delete=django.db.models.deletion.CASCADE, related_name='pen_names', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(help_text='Website context', on_delete=django.db.models.deletion.CASCADE, related_name='pen_names', to='websites.website')),
            ],
            options={
                'verbose_name': 'Pen Name',
                'verbose_name_plural': 'Pen Names',
                'unique_together': {('user', 'website', 'pen_name')},
            },
        ),
        # Indexes
        migrations.AddIndex(
            model_name='profilechangerequest',
            index=models.Index(fields=['user', 'status', '-created_at'], name='users_profil_user_status_created_idx'),
        ),
        migrations.AddIndex(
            model_name='profilechangerequest',
            index=models.Index(fields=['website', 'status'], name='users_profil_website_status_idx'),
        ),
        migrations.AddIndex(
            model_name='profilechangerequest',
            index=models.Index(fields=['change_type', 'status'], name='users_profil_change_type_status_idx'),
        ),
        migrations.AddIndex(
            model_name='writeravatarupload',
            index=models.Index(fields=['user', 'status'], name='users_writer_user_status_idx'),
        ),
        migrations.AddIndex(
            model_name='writeravatarupload',
            index=models.Index(fields=['website', 'status'], name='users_writer_website_status_idx'),
        ),
        migrations.AddIndex(
            model_name='writerprivacysettings',
            index=models.Index(fields=['user', 'website'], name='users_writer_user_website_idx'),
        ),
        migrations.AddIndex(
            model_name='clientprivacysettings',
            index=models.Index(fields=['user', 'website'], name='users_client_user_website_idx'),
        ),
        migrations.AddIndex(
            model_name='penname',
            index=models.Index(fields=['user', 'website', 'is_active'], name='users_penname_user_website_active_idx'),
        ),
        migrations.AddIndex(
            model_name='penname',
            index=models.Index(fields=['pen_name'], name='users_penname_pen_name_idx'),
        ),
    ]

