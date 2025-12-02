# Generated manually
from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('order_configs', '0004_alter_englishtype_code_alter_englishtype_name_and_more'),
        ('pricing_configs', '0001_initial'),
        ('orders', '0009_add_order_templates'),
        ('websites', '0002_add_payment_settings'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderDraft',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(blank=True, max_length=500)),
                ('order_instructions', models.TextField(blank=True)),
                ('number_of_pages', models.PositiveIntegerField(blank=True, null=True)),
                ('number_of_slides', models.PositiveIntegerField(default=0)),
                ('number_of_refereces', models.PositiveIntegerField(default=0)),
                ('deadline', models.DateTimeField(blank=True, null=True)),
                ('estimated_price', models.DecimalField(blank=True, decimal_places=2, help_text='Estimated price calculated from draft', max_digits=10, null=True)),
                ('title', models.CharField(blank=True, help_text='Optional title for the draft', max_length=255)),
                ('notes', models.TextField(blank=True, help_text='Internal notes about this draft')),
                ('is_quote', models.BooleanField(default=False, help_text='Whether this is a quote (not yet an order)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_viewed_at', models.DateTimeField(blank=True, null=True)),
                ('client', models.ForeignKey(limit_choices_to={'role': 'client'}, on_delete=django.db.models.deletion.CASCADE, related_name='order_drafts', to=settings.AUTH_USER_MODEL)),
                ('converted_to_order', models.ForeignKey(blank=True, help_text='The order this draft was converted to', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='source_draft', to='orders.order')),
                ('english_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='order_configs.englishtype')),
                ('preferred_writer', models.ForeignKey(blank=True, limit_choices_to={'role': 'writer'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='draft_preferences', to=settings.AUTH_USER_MODEL)),
                ('type_of_work', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='order_configs.typeofwork')),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_drafts', to='websites.website')),
            ],
            options={
                'verbose_name': 'Order Draft',
                'verbose_name_plural': 'Order Drafts',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderPreset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="Name for this preset (e.g., 'Academic Essay', 'Business Report')", max_length=255)),
                ('description', models.TextField(blank=True, help_text='Optional description of when to use this preset')),
                ('default_spacing', models.CharField(blank=True, max_length=10)),
                ('default_number_of_refereces', models.PositiveIntegerField(default=0)),
                ('style_preferences', models.JSONField(blank=True, default=dict, help_text='Style preferences: tone, formatting, citation style, etc.')),
                ('usage_count', models.PositiveIntegerField(default=0, help_text='Number of times this preset has been used')),
                ('last_used_at', models.DateTimeField(blank=True, null=True, help_text='When this preset was last used')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this preset is active and available')),
                ('is_default', models.BooleanField(default=False, help_text='Whether this is the default preset for the client')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(limit_choices_to={'role': 'client'}, on_delete=django.db.models.deletion.CASCADE, related_name='order_presets', to=settings.AUTH_USER_MODEL)),
                ('default_english_type', models.ForeignKey(blank=True, help_text='Default English style', null=True, on_delete=django.db.models.deletion.SET_NULL, to='order_configs.englishtype')),
                ('default_type_of_work', models.ForeignKey(blank=True, help_text='Default type of work', null=True, on_delete=django.db.models.deletion.SET_NULL, to='order_configs.typeofwork')),
                ('preferred_writer', models.ForeignKey(blank=True, limit_choices_to={'role': 'writer'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='preset_preferences', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_presets', to='websites.website')),
            ],
            options={
                'verbose_name': 'Order Preset',
                'verbose_name_plural': 'Order Presets',
                'ordering': ['-is_default', '-usage_count', '-updated_at'],
            },
        ),
        migrations.AddIndex(
            model_name='orderdraft',
            index=models.Index(fields=['client', 'website'], name='orders_orderdraft_client_idx'),
        ),
        migrations.AddIndex(
            model_name='orderdraft',
            index=models.Index(fields=['is_quote', '-updated_at'], name='orders_orderdraft_is_quote_idx'),
        ),
        migrations.AddIndex(
            model_name='orderpreset',
            index=models.Index(fields=['client', 'website', 'is_active'], name='orders_orderpreset_client_idx'),
        ),
        migrations.AddIndex(
            model_name='orderpreset',
            index=models.Index(fields=['is_default', 'client'], name='orders_orderpreset_is_default_idx'),
        ),
        migrations.AddField(
            model_name='orderdraft',
            name='extra_services',
            field=models.ManyToManyField(blank=True, related_name='order_drafts', to='pricing_configs.additionalservice'),
        ),
        migrations.AddField(
            model_name='orderpreset',
            name='default_extra_services',
            field=models.ManyToManyField(blank=True, related_name='order_presets', to='pricing_configs.additionalservice'),
        ),
    ]

