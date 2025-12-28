# Generated migration for WebsiteIntegrationConfig

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('websites', '0009_add_communication_widget_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebsiteIntegrationConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('integration_type', models.CharField(choices=[
                    ('stripe', 'Stripe'), ('paypal', 'PayPal'), ('razorpay', 'Razorpay'), ('square', 'Square'), ('mollie', 'Mollie'),
                    ('sendgrid', 'SendGrid'), ('mailgun', 'Mailgun'), ('ses', 'AWS SES'), ('postmark', 'Postmark'), ('sparkpost', 'SparkPost'), ('mandrill', 'Mandrill'),
                    ('twilio', 'Twilio'), ('nexmo', 'Vonage (Nexmo)'), ('aws_sns', 'AWS SNS'), ('messagebird', 'MessageBird'),
                    ('s3', 'AWS S3'), ('do_spaces', 'DigitalOcean Spaces'), ('gcs', 'Google Cloud Storage'), ('azure_blob', 'Azure Blob Storage'),
                    ('cloudflare', 'Cloudflare'), ('cloudfront', 'AWS CloudFront'), ('fastly', 'Fastly'),
                    ('google_oauth', 'Google OAuth'), ('facebook_oauth', 'Facebook OAuth'), ('github_oauth', 'GitHub OAuth'), ('linkedin_oauth', 'LinkedIn OAuth'), ('twitter_oauth', 'Twitter OAuth'),
                    ('facebook_pixel', 'Facebook Pixel'), ('pinterest_tag', 'Pinterest Tag'), ('tiktok_pixel', 'TikTok Pixel'), ('hotjar', 'Hotjar'), ('mixpanel', 'Mixpanel'), ('segment', 'Segment'),
                    ('intercom', 'Intercom'), ('zendesk', 'Zendesk'), ('drift', 'Drift'), ('crisp', 'Crisp'),
                    ('pdf_api', 'PDF Generation API'), ('docu_sign', 'DocuSign'), ('hello_sign', 'HelloSign'),
                    ('openai', 'OpenAI'), ('anthropic', 'Anthropic'), ('cohere', 'Cohere'),
                    ('zapier', 'Zapier'), ('make', 'Make (Integromat)'), ('webhook', 'Custom Webhook'),
                    ('custom', 'Custom Integration')
                ], help_text='Type of integration', max_length=50)),
                ('is_active', models.BooleanField(default=True, help_text='Whether this integration is currently active')),
                ('encrypted_api_key', models.TextField(blank=True, help_text='Encrypted API key (encrypted using Fernet)', null=True)),
                ('encrypted_secret_key', models.TextField(blank=True, help_text='Encrypted secret key (encrypted using Fernet)', null=True)),
                ('encrypted_access_token', models.TextField(blank=True, help_text='Encrypted access token (encrypted using Fernet)', null=True)),
                ('config', models.JSONField(blank=True, default=dict, help_text='Public configuration settings (endpoints, regions, etc.)')),
                ('name', models.CharField(blank=True, help_text='Custom name for this integration instance', max_length=255)),
                ('description', models.TextField(blank=True, help_text='Description or notes about this integration')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, help_text='User who created this integration', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_integrations', to=settings.AUTH_USER_MODEL)),
                ('website', models.ForeignKey(help_text='Website this integration belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='integration_configs', to='websites.website')),
            ],
            options={
                'verbose_name': 'Website Integration Configuration',
                'verbose_name_plural': 'Website Integration Configurations',
                'unique_together': {('website', 'integration_type', 'name')},
            },
        ),
        migrations.AddIndex(
            model_name='websiteintegrationconfig',
            index=models.Index(fields=['website', 'integration_type'], name='websites_we_website_123abc_idx'),
        ),
        migrations.AddIndex(
            model_name='websiteintegrationconfig',
            index=models.Index(fields=['website', 'is_active'], name='websites_we_website_456def_idx'),
        ),
    ]

