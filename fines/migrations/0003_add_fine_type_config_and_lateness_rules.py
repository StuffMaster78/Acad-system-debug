# Generated manually to add FineTypeConfig and LatenessFineRule models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fines', '0002_initial'),
        ('websites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LatenessFineRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, help_text='Description of this lateness fine rule')),
                ('calculation_mode', models.CharField(choices=[('percentage', 'Percentage-based'), ('fixed', 'Fixed amount')], default='percentage', max_length=20)),
                ('base_amount', models.DecimalField(decimal_places=2, help_text='Base amount for percentage calculations', max_digits=10, null=True)),
                ('first_hour_percentage', models.DecimalField(decimal_places=2, default=5.0, help_text='Fine percentage for first hour late', max_digits=5)),
                ('second_hour_percentage', models.DecimalField(decimal_places=2, default=10.0, help_text='Fine percentage for second hour late', max_digits=5)),
                ('third_hour_percentage', models.DecimalField(decimal_places=2, default=15.0, help_text='Fine percentage for third hour late', max_digits=5)),
                ('subsequent_hours_percentage', models.DecimalField(decimal_places=2, default=20.0, help_text='Fine percentage for each subsequent hour', max_digits=5)),
                ('daily_rate_percentage', models.DecimalField(decimal_places=2, default=50.0, help_text='Fine percentage if order is more than 24 hours late', max_digits=5)),
                ('max_fine_percentage', models.DecimalField(decimal_places=2, default=100.0, help_text='Maximum fine percentage cap', max_digits=5)),
                ('active', models.BooleanField(default=True)),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lateness_fine_rules', to='websites.website')),
            ],
            options={
                'ordering': ['-start_date'],
            },
        ),
        migrations.CreateModel(
            name='FineTypeConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(help_text='Unique code identifier for this fine type', max_length=50, unique=True)),
                ('name', models.CharField(help_text='Human-readable name for this fine type', max_length=100)),
                ('description', models.TextField(blank=True)),
                ('calculation_type', models.CharField(choices=[('fixed', 'Fixed Amount'), ('percentage', 'Percentage of Base'), ('progressive_hourly', 'Progressive Hourly (Lateness)')], default='fixed', max_length=20)),
                ('fixed_amount', models.DecimalField(blank=True, decimal_places=2, help_text='Fixed fine amount', max_digits=10, null=True)),
                ('percentage', models.DecimalField(blank=True, decimal_places=2, help_text='Fine percentage (0-100)', max_digits=5, null=True)),
                ('base_amount', models.DecimalField(blank=True, decimal_places=2, help_text='Base amount for percentage calculations', max_digits=10, null=True)),
                ('min_amount', models.DecimalField(blank=True, decimal_places=2, help_text='Minimum fine amount', max_digits=10, null=True)),
                ('max_amount', models.DecimalField(blank=True, decimal_places=2, help_text='Maximum fine amount cap', max_digits=10, null=True)),
                ('is_system_defined', models.CharField(choices=[('system', 'System-defined'), ('custom', 'Custom')], default='custom', max_length=20)),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fine_type_configs_created', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(blank=True, help_text='If set, this fine type applies only to this website. If null, applies globally.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fine_type_configs', to='websites.website')),
            ],
            options={
                'ordering': ['code'],
                'unique_together': {('code', 'website')},
            },
        ),
        migrations.AddField(
            model_name='fine',
            name='fine_type_config',
            field=models.ForeignKey(blank=True, help_text='Fine type configuration (preferred over fine_type for new fines)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fines', to='fines.finetypeconfig'),
        ),
    ]

