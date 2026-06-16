"""
Management command: setup_tenants
==================================

Creates Wagtail Site records, page trees, permission groups,
editorial workflows, and the Site ↔ Website bridge for each tenant.

Idempotent — safe to run multiple times.

Usage:
    python manage.py setup_tenants
    python manage.py setup_tenants --workflow=simple # simpler approval chain
"""

from django.core.management.base import BaseCommand, CommandParser
from wagtail.models import Page, Site


TENANTS = [
    {
        "name": "NurseMyGrade",
        "hostname": "nursemygrade.com",
        "slug": "nursemygrade",
    },
    {
        "name": "GradeCrest",
        "hostname": "gradecrest.com",
        "slug": "gradecrest",
    },
    {
        "name": "EssayManiacs",
        "hostname": "essaymaniacs.com",
        "slug": "essaymaniacs",
    },
    {
        "name": "ResearchPaperMate",
        "hostname": "researchpapermate.com",
        "slug": "researchpapermate",
    },
    {
        "name": "WritersCreek",
        "hostname": "writerscreek.com",
        "slug": "writerscreek",
    },
]


class Command(BaseCommand):
    help = (
        "Create Wagtail Site records, page trees, permission groups, "
        "editorial workflows, and Site ↔ Website bridges for all tenants"
    )

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "--workflow",
            choices=["standard", "simple"],
            default="standard",
            help="Workflow type: 'standard' (editor → quality → publish) or 'simple' (admin → publish)",
        )

    def handle(self, *args, **options):
        workflow_type = options["workflow"]

        root_page = Page.objects.filter(depth=1).first()
        if not root_page:
            self.stderr.write("ERROR: Wagtail root page not found. Run migrations first.")
            return

        # Remove default Wagtail welcome page
        welcome = Page.objects.filter(
            depth=2, title="Welcome to your new Wagtail site!"
        ).first()
        if welcome:
            welcome.delete()
            self.stdout.write("Removed default Wagtail welcome page")

        from cms_core.models import (
            TenantHomePage,
            AuthorIndexPage,
            ResourceIndexPage,
        )

        # Lazy imports for optional apps
        BlogIndexPage = self._try_import("cms_blog.models", "BlogIndexPage")
        ServiceIndexPage = self._try_import("cms_service_pages.models", "ServiceIndexPage")

        for tenant_config in TENANTS:
            name = tenant_config["name"]
            hostname = tenant_config["hostname"]
            slug = tenant_config["slug"]

            self.stdout.write(f"\n{'='*50}")
            self.stdout.write(f"Setting up tenant: {name}")
            self.stdout.write(f"{'='*50}")

            # --- 1. Site + Home Page ---
            site = Site.objects.filter(hostname=hostname).first()
            if site:
                self.stdout.write(self.style.SUCCESS(f" Site exists: {hostname}"))
                home_page = site.root_page.specific
            else:
                home_page = TenantHomePage(title=f"{name} Home", slug=slug)
                root_page.add_child(instance=home_page)
                site = Site.objects.create(
                    hostname=hostname,
                    root_page=home_page,
                    is_default_site=False,
                    site_name=name,
                )
                self.stdout.write(f" Created site: {hostname}")

            # --- 2. Child Index Pages ---
            existing_children = set(
                home_page.get_children().values_list("slug", flat=True)
            )

            if BlogIndexPage and "blog" not in existing_children:
                home_page.add_child(instance=BlogIndexPage(title="Blog", slug="blog"))
                self.stdout.write(" Created Blog index page")

            if ServiceIndexPage and "services" not in existing_children:
                home_page.add_child(instance=ServiceIndexPage(title="Services", slug="services"))
                self.stdout.write(" Created Services index page")

            if "authors" not in existing_children:
                home_page.add_child(instance=AuthorIndexPage(title="Authors", slug="authors"))
                self.stdout.write(" Created Authors index page")

            if "resources" not in existing_children:
                home_page.add_child(instance=ResourceIndexPage(title="Resources", slug="resources"))
                self.stdout.write(" Created Resources index page")

            # --- 3. Site ↔ Website Bridge ---
            self._bridge_website(site, hostname)

            # --- 4. Permission Groups ---
            self._setup_permissions(site)

            # --- 5. Editorial Workflow ---
            self._setup_workflow(site, workflow_type)

            self.stdout.write(self.style.SUCCESS(f" {name} setup complete"))

        # Set default site
        if not Site.objects.filter(is_default_site=True).exists():
            first_site = Site.objects.first()
            if first_site:
                first_site.is_default_site = True
                first_site.save()
                self.stdout.write(f"\nSet {first_site.hostname} as default site")

        # --- 6. Health Check ---
        self.stdout.write(f"\n{'='*50}")
        self.stdout.write("Running health check...")
        self._run_health_check()

        self.stdout.write(self.style.SUCCESS("\n All tenants set up successfully"))

    def _try_import(self, module_path, class_name):
        """Try to import a class, return None if the app isn't installed."""
        try:
            import importlib
            module = importlib.import_module(module_path)
            return getattr(module, class_name)
        except (ImportError, AttributeError):
            self.stdout.write(
                self.style.WARNING(f" {module_path}.{class_name} not available — skipping")
            )
            return None

    def _bridge_website(self, site, hostname):
        """Link Wagtail Site to the existing Website model."""
        try:
            from websites.models.websites import Website

            # Prefer exact hostname match (covers https://hostname and bare hostname),
            # fall back to slug-prefix search.
            website = (
                Website.objects.filter(domain__icontains=hostname).first()
                or Website.objects.filter(domain__icontains=hostname.split(".")[0]).first()
            )

            if website:
                # Release stale bridge from any other Website that currently owns this Site
                Website.objects.filter(wagtail_site=site).exclude(pk=website.pk).update(
                    wagtail_site=None
                )

                if website.wagtail_site_id == site.pk:
                    self.stdout.write(f" Bridge already exists: Website #{website.pk} ↔ Site #{site.pk}")
                else:
                    website.wagtail_site = site
                    website.save(update_fields=["wagtail_site"])
                    self.stdout.write(f" Bridged Website #{website.pk} ↔ Site #{site.pk}")
            else:
                self.stdout.write(
                    self.style.WARNING(f" No Website found matching '{hostname}' — bridge not created")
                )
        except ImportError:
            self.stdout.write(self.style.WARNING(" websites app not found — bridge skipped"))
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f" Bridge error: {exc}"))

    def _setup_permissions(self, site):
        """Create per-tenant permission groups."""
        try:
            from cms_core.services.permissions_service import TenantPermissionsService

            groups = TenantPermissionsService.setup_tenant_permissions(site)
            for role, group in groups.items():
                self.stdout.write(f" Permission group: {group.name}")
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f" Permission setup error: {exc}"))

    def _setup_workflow(self, site, workflow_type):
        """Create editorial workflow for the tenant."""
        try:
            from cms_core.services.workflow_service import WorkflowService

            if workflow_type == "simple":
                workflow = WorkflowService.setup_simple_workflow(site)
            else:
                workflow = WorkflowService.setup_editorial_workflow(site)

            self.stdout.write(f" Workflow: {workflow.name}")
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f" Workflow setup error: {exc}"))

    def _run_health_check(self):
        """Validate all bridges and permissions."""
        try:
            from cms_core.services.tenant_service import validate_all_tenants_bridged

            issues = validate_all_tenants_bridged()
            if issues:
                for issue in issues:
                    self.stdout.write(self.style.WARNING(f" {issue}"))
            else:
                self.stdout.write(self.style.SUCCESS(" All tenant bridges verified "))
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f" Health check error: {exc}"))
