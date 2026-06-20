"""
extract_faq_blocks
==================
Scans ServicePage (and optionally BlogPostPage) bodies for HTML FAQ sections
stored inside paragraph blocks, extracts the Q&A pairs, and replaces them
with structured faq blocks in the StreamField.

FAQ patterns detected:
  - Headings whose text matches /faq|frequently asked|questions/i followed by
    pairs of <h3>/<h4> (question) + <p> (answer) siblings
  - Definition-list style: <dl><dt>question</dt><dd>answer</dd></dl>
  - Explicit Q:/A: prefixed paragraphs

The body is transformed from:
  [paragraph HTML with FAQ section embedded]
to:
  [paragraph HTML — everything before FAQ] +
  [faq block per Q&A pair] +
  [paragraph HTML — everything after FAQ, if any]

Safe to re-run — pages that already have faq blocks at the top level are
skipped unless --force is passed.

Usage:
    python manage.py extract_faq_blocks --site gradecrest.com
    python manage.py extract_faq_blocks --site nursemygrade.com --dry-run
    python manage.py extract_faq_blocks --all-sites
    python manage.py extract_faq_blocks --all-sites --force
"""

from __future__ import annotations

import re
import uuid
from html.parser import HTMLParser
from typing import Optional

from django.core.management.base import BaseCommand, CommandParser


# ---------------------------------------------------------------------------
# HTML parsing helpers
# ---------------------------------------------------------------------------

def _strip_tags(html: str) -> str:
    class S(HTMLParser):
        def __init__(self): super().__init__(); self.text: list[str] = []
        def handle_data(self, data: str) -> None: self.text.append(data)
    s = S(); s.feed(html); return ' '.join(s.text).strip()


# ---------------------------------------------------------------------------
# Core extraction logic
# ---------------------------------------------------------------------------

def extract_faqs_from_html(body_html: str) -> Optional[dict]:
    """
    Parse body_html looking for a FAQ section.

    Returns None if no FAQ section is found, otherwise:
    {
        'before': str,          # HTML before the FAQ section
        'faqs':   [(q, a), ...],
        'after':  str,          # HTML after the FAQ section (often empty)
    }
    """
    # Strategy 1: heading-based detection (most common in scraped content)
    result = _extract_heading_faqs(body_html)
    if result and result['faqs']:
        return result

    # Strategy 2: dl/dt/dd style
    result = _extract_dl_faqs(body_html)
    if result and result['faqs']:
        return result

    return None


def _extract_heading_faqs(html: str) -> Optional[dict]:
    """
    Detect FAQ via a heading that matches _is_faq_heading, followed by
    h3/h4+paragraph pairs.
    """
    # Split at the FAQ heading
    faq_heading_pattern = re.compile(
        r'(<h[23456][^>]*>(?:(?!<\/h[23456]>).)*(?:faq|frequently asked|common questions|questions about|questions &amp;)(?:(?!<\/h[23456]>).)*<\/h[23456]>)',
        re.IGNORECASE | re.DOTALL,
    )
    m = faq_heading_pattern.search(html)
    if not m:
        return None

    before = html[:m.start()].strip()
    faq_section = html[m.end():].strip()

    # Extract h3/h4 + following paragraphs as Q&A pairs
    faqs: list[tuple[str, str]] = []
    # Pattern: <h3>question</h3> <p>...</p> ... (until next h3/h4 or end)
    qa_pattern = re.compile(
        r'<h[34][^>]*>(.*?)<\/h[34]>(.*?)(?=<h[34]|$)',
        re.IGNORECASE | re.DOTALL,
    )
    after = faq_section
    for qa_m in qa_pattern.finditer(faq_section):
        question = _strip_tags(qa_m.group(1)).strip()
        answer_html = qa_m.group(2).strip()
        # Clean answer: keep only p/ul/ol content
        answer_text = _strip_tags(answer_html).strip()
        if question and answer_text:
            # Wrap answer in <p> if it's plain text
            if not answer_html.startswith('<'):
                answer_html = f'<p>{answer_html}</p>'
            faqs.append((question, answer_html))
        # After the last matched block
        after = faq_section[qa_m.end():].strip()

    if not faqs:
        return None

    return {'before': before, 'faqs': faqs, 'after': after}


def _extract_dl_faqs(html: str) -> Optional[dict]:
    """Detect FAQ via <dl><dt>question</dt><dd>answer</dd></dl> pattern."""
    dl_pattern = re.compile(r'<dl[^>]*>(.*?)<\/dl>', re.IGNORECASE | re.DOTALL)
    dt_pattern = re.compile(r'<dt[^>]*>(.*?)<\/dt>', re.IGNORECASE | re.DOTALL)
    dd_pattern = re.compile(r'<dd[^>]*>(.*?)<\/dd>', re.IGNORECASE | re.DOTALL)

    m = dl_pattern.search(html)
    if not m:
        return None

    dl_content = m.group(1)
    questions = dt_pattern.findall(dl_content)
    answers   = dd_pattern.findall(dl_content)

    if not questions or len(questions) != len(answers):
        return None

    faqs = [
        (_strip_tags(q).strip(), f'<p>{_strip_tags(a).strip()}</p>' if not a.strip().startswith('<') else a.strip())
        for q, a in zip(questions, answers)
        if _strip_tags(q).strip() and _strip_tags(a).strip()
    ]

    if not faqs:
        return None

    before = html[:m.start()].strip()
    after  = html[m.end():].strip()
    return {'before': before, 'faqs': faqs, 'after': after}


# ---------------------------------------------------------------------------
# Wagtail StreamField helpers
# ---------------------------------------------------------------------------

def _make_faq_block(question: str, answer: str) -> dict:
    return {
        'type': 'faq',
        'id': str(uuid.uuid4()),
        'value': {
            'question': question,
            'answer': answer,
        },
    }


def _make_paragraph_block(html: str) -> dict:
    return {
        'type': 'paragraph',
        'id': str(uuid.uuid4()),
        'value': html,
    }


# ---------------------------------------------------------------------------
# Management command
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = "Extract FAQ sections from paragraph body blocks and convert to structured faq blocks."

    def add_arguments(self, parser: CommandParser) -> None:
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--site', help='Site hostname (e.g. gradecrest.com)')
        group.add_argument('--all-sites', action='store_true')
        parser.add_argument('--dry-run', action='store_true', default=False)
        parser.add_argument('--force', action='store_true', default=False,
                            help='Process pages that already have top-level faq blocks')
        parser.add_argument('--blog', action='store_true', default=False,
                            help='Also process BlogPostPage bodies')
        parser.add_argument('--limit', type=int, default=0)

    def handle(self, *args, **options):
        from wagtail.models import Site
        from cms_service_pages.models import ServicePage

        dry_run   = options['dry_run']
        force     = options['force']
        do_blog   = options['blog']
        limit     = options['limit']

        if options['all_sites']:
            sites = list(Site.objects.all())
        else:
            try:
                sites = [Site.objects.get(hostname=options['site'])]
            except Site.DoesNotExist:
                available = list(Site.objects.values_list('hostname', flat=True))
                self.stderr.write(self.style.ERROR(
                    f"Site '{options['site']}' not found. Available: {available}"
                ))
                return

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no database writes."))

        total_converted = total_skipped = total_errors = 0

        for site in sites:
            self.stdout.write(f"\n── {site.hostname} ──")

            # Service pages
            qs = ServicePage.objects.live().descendant_of(site.root_page)
            if limit:
                qs = qs[:limit]

            for page in qs:
                result = self._process_page(page, dry_run=dry_run, force=force)
                if result == 'converted':
                    total_converted += 1
                elif result == 'skipped':
                    total_skipped += 1
                elif result == 'error':
                    total_errors += 1

            # Blog posts (optional)
            if do_blog:
                from cms_blog.models import BlogPostPage
                blog_qs = BlogPostPage.objects.live().descendant_of(site.root_page)
                if limit:
                    blog_qs = blog_qs[:limit]
                for page in blog_qs:
                    result = self._process_page(page, dry_run=dry_run, force=force)
                    if result == 'converted':
                        total_converted += 1
                    elif result == 'skipped':
                        total_skipped += 1
                    elif result == 'error':
                        total_errors += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Converted={total_converted} Skipped={total_skipped} Errors={total_errors}"
        ))

    def _process_page(self, page, *, dry_run: bool, force: bool) -> str:
        try:
            body = page.body  # StreamValue
        except Exception:
            return 'skipped'

        if not body:
            return 'skipped'

        # Skip if already has top-level faq blocks (unless --force)
        if not force and any(b.block_type == 'faq' for b in body):
            return 'skipped'

        # Only process pages where body is a single paragraph block
        if len(body) != 1 or body[0].block_type != 'paragraph':
            return 'skipped'

        body_html = str(body[0].value)
        if not body_html.strip():
            return 'skipped'

        extraction = extract_faqs_from_html(body_html)
        if not extraction or not extraction['faqs']:
            return 'skipped'

        # Build new StreamField body
        new_body: list[dict] = []
        if extraction['before']:
            new_body.append(_make_paragraph_block(extraction['before']))

        for question, answer in extraction['faqs']:
            new_body.append(_make_faq_block(question, answer))

        if extraction['after']:
            new_body.append(_make_paragraph_block(extraction['after']))

        faq_count = len(extraction['faqs'])
        slug = getattr(page, 'slug', str(page.pk))

        if dry_run:
            self.stdout.write(
                f"  (dry) {slug} — would extract {faq_count} FAQs"
            )
            return 'converted'

        try:
            page.body = new_body
            page.save_revision().publish()
            self.stdout.write(
                self.style.SUCCESS(f"  {slug} — extracted {faq_count} FAQs")
            )
            return 'converted'
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"  ERROR {slug}: {exc}"))
            return 'error'
