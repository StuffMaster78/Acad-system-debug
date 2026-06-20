"""
import_blog_posts — import article content into Wagtail BlogPostPage

Reads a JSON file of articles and creates (or optionally updates) published
BlogPostPage objects under the site's BlogIndexPage.

JSON schema (each item):
    {
        "slug":               "my-article-slug",
        "title":              "Article Title",
        "excerpt":            "Short description ...",
        "body_html":          "<p>Full HTML body ...</p>",
        "category":           "Category Name",
        "tags":               ["tag1", "tag2"],
        "author_name":        "Jane Doe",
        "author_slug":        "jane-doe",
        "author_credentials": "PhD, English Literature",
        "author_bio":         "Jane Doe is ...",
        "published_at":       "2024-03-15",
        "seo_title":          "Optional SEO title",
        "search_description": "Optional meta description",
        "reading_time":       8
    }

Fields "seo_title", "search_description", "reading_time", "author_credentials",
"author_bio", "author_slug" are all optional — sensible defaults are applied.

Usage:
    python manage.py import_blog_posts --site gradecrest.com --file /tmp/articles.json
    python manage.py import_blog_posts --site gradecrest.com --file articles.json --update
    python manage.py import_blog_posts --site gradecrest.com --file articles.json --publish

The --update flag overwrites body/excerpt on existing posts.
The --publish flag (default True) makes imported posts live immediately.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.utils.text import slugify


class Command(BaseCommand):
    help = "Import blog posts from a JSON file into Wagtail for a given site."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--site",
            required=True,
            help="Site domain (e.g. gradecrest.com). Used to locate the Wagtail Site and BlogIndexPage.",
        )
        parser.add_argument(
            "--file",
            required=True,
            help="Path to JSON file containing articles.",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            default=False,
            help="Update body/excerpt on posts that already exist (default: skip).",
        )
        parser.add_argument(
            "--publish",
            action="store_true",
            default=True,
            help="Publish pages immediately (default: True).",
        )
        parser.add_argument(
            "--no-publish",
            action="store_false",
            dest="publish",
            help="Import as draft instead of publishing.",
        )
        parser.add_argument(
            "--default-author",
            default=None,
            help="Slug of a fallback Author to use when article has no author_name.",
        )

    def handle(self, *args, **options):
        from wagtail.models import Page, Site
        from cms_blog.models import BlogIndexPage, BlogPostPage
        from cms_core.models import BlogCategory, BlogTag
        from cms_authors.models import Author

        site_domain = options["site"]
        json_path = options["file"]
        do_update = options["update"]
        do_publish = options["publish"]
        default_author_slug = options["default_author"]

        # ── Load JSON ───────────────────────────────────────────────────────────
        if not os.path.exists(json_path):
            raise CommandError(f"File not found: {json_path}")
        with open(json_path, encoding="utf-8") as f:
            articles = json.load(f)

        if not isinstance(articles, list):
            raise CommandError("JSON must be a top-level array of article objects.")

        self.stdout.write(f"Loaded {len(articles)} articles from {json_path}")

        # ── Resolve Wagtail Site ─────────────────────────────────────────────────
        try:
            wagtail_site = Site.objects.get(hostname=site_domain)
        except Site.DoesNotExist:
            # Try without www/subdomain variants
            hostname_bare = site_domain.replace("www.", "")
            wagtail_site = (
                Site.objects.filter(hostname__icontains=hostname_bare).first()
            )
            if not wagtail_site:
                raise CommandError(
                    f"Wagtail Site not found for domain '{site_domain}'. "
                    f"Available: {list(Site.objects.values_list('hostname', flat=True))}"
                )

        self.stdout.write(f"Using Wagtail site: {wagtail_site}")

        # ── Find BlogIndexPage ───────────────────────────────────────────────────
        blog_index = (
            BlogIndexPage.objects.live()
            .descendant_of(wagtail_site.root_page)
            .first()
        )
        if not blog_index:
            raise CommandError(
                f"No live BlogIndexPage found under '{wagtail_site.root_page}'. "
                "Create one via Wagtail admin first."
            )
        self.stdout.write(f"BlogIndexPage: {blog_index.title!r} (id={blog_index.pk})")

        # ── Default author fallback ──────────────────────────────────────────────
        default_author = None
        if default_author_slug:
            default_author = Author.objects.filter(slug=default_author_slug).first()

        # ── Import loop ──────────────────────────────────────────────────────────
        created = updated = skipped = errors = 0

        for idx, article in enumerate(articles, start=1):
            try:
                result = self._import_article(
                    article=article,
                    blog_index=blog_index,
                    wagtail_site=wagtail_site,
                    do_update=do_update,
                    do_publish=do_publish,
                    default_author=default_author,
                )
                if result == "created":
                    created += 1
                elif result == "updated":
                    updated += 1
                else:
                    skipped += 1
            except Exception as exc:
                errors += 1
                slug = article.get("slug", f"[article {idx}]")
                self.stderr.write(self.style.ERROR(f"  ERROR {slug}: {exc}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Created={created} Updated={updated} Skipped={skipped} Errors={errors}"
            )
        )

    # ── per-article logic ────────────────────────────────────────────────────────

    def _import_article(
        self,
        *,
        article: dict,
        blog_index,
        wagtail_site,
        do_update: bool,
        do_publish: bool,
        default_author,
    ) -> str:
        from wagtail.models import Page
        from cms_blog.models import BlogPostPage
        from cms_core.models import BlogCategory, BlogTag
        from cms_authors.models import Author

        slug = article.get("slug") or slugify(article.get("title", ""))
        title = article.get("title", slug)

        if not slug:
            raise ValueError("Article has no slug or title.")

        # ── Check if exists ──────────────────────────────────────────────────────
        existing = BlogPostPage.objects.filter(slug=slug).first()
        if existing and not do_update:
            self.stdout.write(f"  SKIP  {slug}")
            return "skipped"

        # ── Resolve author ───────────────────────────────────────────────────────
        author = self._get_or_create_author(article, default_author, wagtail_site)

        # ── Resolve category ─────────────────────────────────────────────────────
        category = self._get_or_create_category(article.get("category"), blog_index, wagtail_site)

        # ── Build StreamField body ───────────────────────────────────────────────
        body_html = article.get("body_html", "") or article.get("body", "")
        body_blocks = self._html_to_body(body_html)

        # ── Tags ─────────────────────────────────────────────────────────────────
        tag_objects = []
        for tag_name in article.get("tags", []):
            tag_slug = slugify(tag_name)
            tag, _ = BlogTag.objects.get_or_create(slug=tag_slug, defaults={"name": tag_name})
            tag_objects.append(tag)

        # ── Published date ───────────────────────────────────────────────────────
        published_at = self._parse_date(article.get("published_at"))

        # ── Create or update ─────────────────────────────────────────────────────
        if existing:
            existing.title = title
            existing.excerpt = article.get("excerpt", "")[:300]
            existing.body = body_blocks
            existing.seo_title = article.get("seo_title", title)
            existing.search_description = article.get("search_description", "")
            if do_publish:
                existing.save_revision().publish()
            else:
                existing.save()
            # Backfill original publication date when provided
            if published_at:
                existing.refresh_from_db()
                existing.first_published_at = published_at
                existing.last_published_at = published_at
                existing.save(update_fields=["first_published_at", "last_published_at"])
            self.stdout.write(f"  UPDATE {slug}")
            return "updated"

        # ── Create new page ──────────────────────────────────────────────────────
        page = BlogPostPage(
            title=title,
            slug=slug,
            seo_title=article.get("seo_title", title),
            search_description=article.get("search_description", article.get("excerpt", ""))[:255],
            excerpt=article.get("excerpt", "")[:300],
            body=body_blocks,
            primary_author=author,
            category=category,
        )

        blog_index.add_child(instance=page)

        if tag_objects:
            page.tags.set(tag_objects)
            page.save()

        if do_publish:
            revision = page.save_revision()
            revision.publish()

        if published_at:
            page.refresh_from_db()
            page.first_published_at = published_at
            page.last_published_at = published_at
            page.save(update_fields=["first_published_at", "last_published_at"])

        self.stdout.write(f"  CREATE {slug}")
        return "created"

    # ── helpers ──────────────────────────────────────────────────────────────────

    def _get_or_create_author(self, article: dict, default_author, wagtail_site) -> "Author":
        from cms_authors.models import Author

        author_name = article.get("author_name")
        author_slug = article.get("author_slug") or (slugify(author_name) if author_name else None)

        if author_slug:
            author = Author.objects.filter(slug=author_slug, site=wagtail_site).first()
            if not author:
                author = Author.objects.create(
                    site=wagtail_site,
                    name=author_name or author_slug,
                    slug=author_slug,
                    credentials=article.get("author_credentials", ""),
                    bio=article.get("author_bio", ""),
                )
            return author

        if default_author:
            return default_author

        # Last resort: platform editorial team
        fallback_slug = "platform-editorial-team"
        author, _ = Author.objects.get_or_create(
            slug=fallback_slug,
            site=wagtail_site,
            defaults={
                "name": "Editorial Team",
                "credentials": "",
                "bio": "",
            },
        )
        return author

    def _get_or_create_category(self, category_name: str | None, blog_index, wagtail_site):
        if not category_name:
            return None
        from cms_core.models import BlogCategory

        slug = slugify(category_name)
        cat = BlogCategory.objects.filter(slug=slug, site=wagtail_site).first()
        if not cat:
            cat = BlogCategory.objects.create(slug=slug, name=category_name, site=wagtail_site)
        return cat

    @staticmethod
    def _html_to_body(html: str) -> list:
        """
        Wrap the full HTML body in a single richtext StreamField block.
        Wagtail's RichTextBlock accepts HTML directly.
        If the HTML is empty, return an empty list.
        """
        html = html.strip() if html else ""
        if not html:
            return []
        return [{"type": "richtext", "value": html}]

    @staticmethod
    def _parse_date(date_str: str | None):
        if not date_str:
            return None
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z"):
            try:
                dt = datetime.strptime(date_str, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue
        return None
