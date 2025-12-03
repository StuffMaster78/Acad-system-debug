from decimal import Decimal

from django.db import migrations


def set_guest_checkout_safe_defaults(apps, schema_editor):
    Website = apps.get_model("websites", "Website")

    for website in Website.objects.all():
        # Ensure email verification is enabled for all guests
        if getattr(website, "guest_requires_email_verification", True) is not True:
            website.guest_requires_email_verification = True

        # Set a conservative cap for guest orders if none is set
        if getattr(website, "guest_max_order_amount", None) is None:
            website.guest_max_order_amount = Decimal("150.00")

        # Block ultra‑urgent guest orders by default
        if not getattr(website, "guest_block_urgent_before_hours", 0):
            website.guest_block_urgent_before_hours = 12

        # Magic links valid for three days by default
        if not getattr(website, "guest_magic_link_ttl_hours", 0):
            website.guest_magic_link_ttl_hours = 72

        website.save(update_fields=[
            "guest_requires_email_verification",
            "guest_max_order_amount",
            "guest_block_urgent_before_hours",
            "guest_magic_link_ttl_hours",
        ])


def noop_reverse(apps, schema_editor):
    # We don't attempt to revert defaults automatically.
    # Admins can override per‑website settings from the UI.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("websites", "0007_website_guest_block_urgent_before_hours_and_more"),
    ]

    operations = [
        migrations.RunPython(set_guest_checkout_safe_defaults, noop_reverse),
    ]


