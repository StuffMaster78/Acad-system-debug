# Generated by Django 5.1.6 on 2025-02-22 03:37

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('websites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, help_text='Soft delete timestamp', null=True)),
                ('referral_code', models.CharField(blank=True, help_text='Unique referral code used by the referee.', max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('registration_bonus_credited', models.BooleanField(default=False, help_text='Has the registration bonus been credited?')),
                ('first_order_bonus_credited', models.BooleanField(default=False, help_text='Has the first-order bonus been credited?')),
                ('created_by', models.ForeignKey(blank=True, help_text='User who created the record', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s_set', to=settings.AUTH_USER_MODEL)),
                ('referee', models.OneToOneField(help_text='The user who was referred.', on_delete=django.db.models.deletion.CASCADE, related_name='referred_by', to=settings.AUTH_USER_MODEL)),
                ('referrer', models.ForeignKey(help_text='The user who referred someone else.', on_delete=django.db.models.deletion.CASCADE, related_name='referrals', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, help_text='User who last updated the record', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_%(class)s_set', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(blank=True, help_text='Website this record is associated with', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_set', to='websites.website')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReferralBonusConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, help_text='Soft delete timestamp', null=True)),
                ('registration_bonus', models.DecimalField(decimal_places=2, default=0.0, help_text='Bonus amount for successful referee registration.', max_digits=10)),
                ('first_order_bonus', models.DecimalField(decimal_places=2, default=0.0, help_text="Bonus amount for referee's first order.", max_digits=10)),
                ('referee_discount', models.DecimalField(decimal_places=2, default=0.0, help_text="Discount for the referee's first order.", max_digits=10)),
                ('created_by', models.ForeignKey(blank=True, help_text='User who created the record', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s_set', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, help_text='User who last updated the record', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_%(class)s_set', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(blank=True, help_text='Website this record is associated with', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_set', to='websites.website')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReferralCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, help_text='Soft delete timestamp', null=True)),
                ('code', models.CharField(help_text='Unique referral code.', max_length=50, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, help_text='User who created the record', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s_set', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, help_text='User who last updated the record', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_%(class)s_set', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(help_text='The user associated with this referral code.', on_delete=django.db.models.deletion.CASCADE, related_name='referral_code', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(blank=True, help_text='Website this record is associated with', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_set', to='websites.website')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
