from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments_processor", "0008_add_gateway_config"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentgatewayconfig",
            name="secret_key_env_var",
            field=models.CharField(
                blank=True,
                default="",
                max_length=128,
                help_text=(
                    "Name of the environment variable that holds this site's Stripe secret key "
                    "(e.g. STRIPE_SECRET_KEY_NURSEMYGRADE). "
                    "Leave blank to use the platform default STRIPE_SECRET_KEY."
                ),
            ),
        ),
        migrations.AddField(
            model_name="paymentgatewayconfig",
            name="webhook_secret_env_var",
            field=models.CharField(
                blank=True,
                default="",
                max_length=128,
                help_text=(
                    "Name of the environment variable that holds this site's Stripe webhook "
                    "signing secret (e.g. STRIPE_WEBHOOK_SECRET_NURSEMYGRADE). "
                    "Leave blank to use the platform default STRIPE_WEBHOOK_SECRET."
                ),
            ),
        ),
        migrations.AddField(
            model_name="paymentgatewayconfig",
            name="statement_descriptor",
            field=models.CharField(
                blank=True,
                default="",
                max_length=22,
                help_text=(
                    "Statement descriptor sent to Stripe for every payment on this site — "
                    "what appears on the cardholder's bank statement. Max 22 chars, "
                    "Latin characters only, no < > \\ ' \" * characters. "
                    "Leave blank to use the Stripe account default."
                ),
            ),
        ),
        migrations.AlterField(
            model_name="paymentgatewayconfig",
            name="webhook_endpoint",
            field=models.CharField(
                default="/api/payments/webhooks/stripe/",
                max_length=255,
                help_text=(
                    "Full path registered in the Stripe dashboard for this site. "
                    "For per-site routing use /api/payments/webhooks/stripe/<site-slug>/."
                ),
            ),
        ),
    ]
