"""
Management command to seed essaymaniacs.com as a client portal tenant.

Run once per environment:
    python manage.py seed_essaymaniacs
    python manage.py seed_essaymaniacs --domain https://essaymaniacs.com
    python manage.py seed_essaymaniacs --domain http://localhost:3005  # dev

This is safe to re-run — all creates use update_or_create.
"""
from __future__ import annotations

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed essaymaniacs.com Website, WebsiteBranding, and client PortalDefinition."

    def add_arguments(self, parser):
        parser.add_argument(
            "--domain",
            default="https://essaymaniacs.com",
            help="Marketing domain for the website record (default: https://essaymaniacs.com)",
        )
        parser.add_argument(
            "--app-domain",
            default="https://app.essaymaniacs.com",
            help="Portal SPA subdomain (default: https://app.essaymaniacs.com)",
        )

    def handle(self, *args, **options):
        domain     = options["domain"].rstrip("/")
        app_domain = options["app_domain"].rstrip("/")

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"\nSeeding EssayManiacs tenant ({domain})\n"
        ))

        website = self._seed_website(domain)
        self._seed_branding(website)
        self._seed_portal()
        self._seed_cors_reminder(domain, app_domain)

        self.stdout.write(self.style.SUCCESS("\nDone. EssayManiacs tenant is ready.\n"))

    def _seed_website(self, domain: str):
        from websites.models.websites import Website

        website, created = Website.objects.update_or_create(
            domain=domain,
            defaults={
                "name": "EssayManiacs",
                "slug": "essaymaniacs",
                "is_active": True,
                "contact_email": "support@essaymaniacs.com",
            },
        )
        self._log("Website", website.name, created)
        return website

    def _seed_branding(self, website):
        from websites.models.website_branding import WebsiteBranding

        branding, created = WebsiteBranding.objects.update_or_create(
            website=website,
            defaults={
                "brand_name": "EssayManiacs",
                "tagline": "Essays and academic writing by obsessive word nerds.",
                "homepage_headline": "Essays & Academic Papers Written by Real Experts",
                "homepage_subheadline": (
                    "Human-written essays from $13/page — term papers, "
                    "dissertations, case studies, and more across 100+ subjects."
                ),
                "primary_color": "#7c3aed",     # violet-600
                "secondary_color": "#4c1d95",   # violet-900
                "accent_color": "#a78bfa",      # violet-400
                "payment_processor_name": "OrderBridge Payments",
                "payment_statement_descriptor": "ORDERBRIDGE PAYMENTS",
                "payment_client_disclosure_text": (
                    "Your payment is securely processed by OrderBridge Payments, "
                    "our authorised billing partner. Your bank or card statement may "
                    "show 'ORDERBRIDGE PAYMENTS'."
                ),
                "payment_requires_acknowledgement": True,
                "is_public": True,
            },
        )
        self._log("WebsiteBranding", branding.brand_name, created)
        return branding

    def _seed_portal(self):
        from accounts.models.portal_definition import PortalDefinition

        portal, created = PortalDefinition.objects.get_or_create(
            code="client_portal",
            defaults={
                "name": "Client Portal",
                "domain": "localhost",
                "is_active": True,
            },
        )
        self._log("PortalDefinition (client_portal)", portal.domain, created)

    def _seed_cors_reminder(self, domain: str, app_domain: str):
        bare     = domain.replace("https://", "").replace("http://", "")
        app_bare = app_domain.replace("https://", "").replace("http://", "")
        self.stdout.write(
            self.style.WARNING(
                f"\nAdd these to your production .env:\n\n"
                f"  ALLOWED_HOSTS=...,{bare},{app_bare}\n"
                f"  CORS_ALLOWED_ORIGINS=...,{domain},{app_domain}\n"
                f"  CSRF_TRUSTED_ORIGINS=...,{domain},{app_domain}\n"
            )
        )

    def _log(self, model: str, identifier: str, created: bool):
        verb = "Created" if created else "Updated"
        self.stdout.write(f"  {verb:8s} {model}: {identifier}")
