# Generated manually for reviews_system app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('websites', '0001_initial'),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebsiteReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('comment', models.TextField(blank=True)),
                ('origin', models.CharField(choices=[('client', 'Client'), ('admin', 'Admin')], default='client', max_length=20)),
                ('is_approved', models.BooleanField(default=False)),
                ('is_shadowed', models.BooleanField(default=False)),
                ('is_flagged', models.BooleanField(default=False)),
                ('flag_reason', models.TextField(blank=True)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='websitereview_reviews_given', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='websites.website')),
            ],
            options={
                'ordering': ['-submitted_at'],
                'unique_together': {('reviewer', 'website')},
            },
        ),
        migrations.CreateModel(
            name='WriterReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('comment', models.TextField(blank=True)),
                ('origin', models.CharField(choices=[('client', 'Client'), ('admin', 'Admin')], default='client', max_length=20)),
                ('is_approved', models.BooleanField(default=False)),
                ('is_shadowed', models.BooleanField(default=False)),
                ('is_flagged', models.BooleanField(default=False)),
                ('flag_reason', models.TextField(blank=True)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='writerreview_reviews_given', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='writer_reviews', to='websites.website')),
                ('writer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='writer_reviews', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-submitted_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('comment', models.TextField(blank=True)),
                ('origin', models.CharField(choices=[('client', 'Client'), ('admin', 'Admin')], default='client', max_length=20)),
                ('is_approved', models.BooleanField(default=False)),
                ('is_shadowed', models.BooleanField(default=False)),
                ('is_flagged', models.BooleanField(default=False)),
                ('flag_reason', models.TextField(blank=True)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='orders.order')),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orderreview_reviews_given', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_reviews', to='websites.website')),
                ('writer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_reviews_written_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-submitted_at'],
                'unique_together': {('reviewer', 'order')},
            },
        ),
    ]

