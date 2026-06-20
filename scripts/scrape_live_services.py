#!/usr/bin/env python3
"""
scrape_live_services.py
=======================
Scrapes long-form service pages from a live site and writes a JSON file
compatible with the import_service_pages management command.

Reads URLs from each site's service sitemap, fetches the page HTML,
and extracts title/slug/headline/meta/body into the import schema.

Supported sites:
  gradecrest.com        — section.page_content
  nursemygrade.com      — section.blog_body
  researchpapermate.com — section.page_content  (same template as GC)
  essaymaniacs.com      — section.page_conts

Usage:
    python3 scripts/scrape_live_services.py --site gradecrest.com --out /tmp/gc_services.json
    python3 scripts/scrape_live_services.py --site nursemygrade.com --out /tmp/nmg_services.json --delay 0.5
    python3 scripts/scrape_live_services.py --site essaymaniacs.com --out /tmp/em_services.json
    python3 scripts/scrape_live_services.py --site researchpapermate.com --out /tmp/rpm_services.json

Then import with:
    docker compose cp /tmp/gc_services.json web:/tmp/gc_services.json
    docker compose exec web python manage.py import_service_pages \\
        --site gradecrest.com --file /tmp/gc_services.json

Re-run with --update to refresh body on already-imported pages.
Use --resume to skip slugs already written to --out (crash recovery).
"""

from __future__ import annotations

import argparse
import html as html_module
import json
import os
import re
import sys
import time
import urllib.request
from html.parser import HTMLParser
from typing import Optional
from urllib.parse import urlparse
from xml.etree import ElementTree as ET


# ---------------------------------------------------------------------------
# Site profiles
# ---------------------------------------------------------------------------

SITE_PROFILES: dict[str, dict] = {
    "gradecrest.com": {
        "sitemap_url": "https://gradecrest.com/services-sitemap.xml",
        "parser": "gc_rpm",
        "skip_paths": {"/services", "/services/", "/services.php"},
    },
    "nursemygrade.com": {
        "sitemap_url": "https://nursemygrade.com/sitemap-services.xml",
        "parser": "nmg",
        "skip_paths": {"/services", "/services/", "/services.php"},
    },
    "researchpapermate.com": {
        "sitemap_url": "https://researchpapermate.com/services-sitemap.xml",
        "parser": "gc_rpm",
        "skip_paths": {"/services", "/services/", "/services.php"},
    },
    "essaymaniacs.com": {
        "sitemap_url": "https://essaymaniacs.com/sitemap-services.xml",
        "parser": "em",
        "skip_paths": {"/services", "/services/", "/services.php"},
    },
}


# ---------------------------------------------------------------------------
# Minimal HTML utilities (stdlib only)
# ---------------------------------------------------------------------------

class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def get_text(self) -> str:
        return " ".join(self._parts).strip()


def strip_tags(html: str) -> str:
    p = _TextExtractor()
    p.feed(html)
    return p.get_text()


def _fetch(url: str, retries: int = 3, timeout: int = 20) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; ServicePageImporter/1.0; "
            "+https://github.com/your-org/writing-system)"
        ),
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    }
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
                ct = resp.headers.get("Content-Type", "")
                m = re.search(r"charset=([^\s;]+)", ct)
                enc = m.group(1).strip() if m else "utf-8"
                return raw.decode(enc, errors="replace")
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)
    return ""


def _fetch_sitemap_urls(sitemap_url: str) -> list[str]:
    xml = _fetch(sitemap_url)
    xml = re.sub(r'\s+xmlns(?::\w+)?="[^"]*"', "", xml)
    xml = re.sub(r'\s+xsi:[a-zA-Z]+="[^"]*"', "", xml)
    xml = re.sub(r'<(\w+):', "<", xml)
    xml = re.sub(r'</(\w+):', "</", xml)
    xml = re.sub(r'<\?xml-stylesheet[^?]*\?>', "", xml)
    root = ET.fromstring(xml)
    urls: list[str] = []
    for sm in root.findall(".//sitemap/loc"):
        if sm.text:
            urls.extend(_fetch_sitemap_urls(sm.text.strip()))
    for loc in root.findall(".//url/loc"):
        if loc.text:
            urls.append(loc.text.strip())
    return urls


# ---------------------------------------------------------------------------
# Common helpers
# ---------------------------------------------------------------------------

def _slug_from_url(url: str) -> str:
    """Return a clean slug from a URL, stripping file extensions (.php, .html, etc.)."""
    path = urlparse(url).path.strip("/")
    last = path.split("/")[-1] if "/" in path else path
    # Strip extensions so essay-writing.php → essay-writing
    last = re.sub(r"\.[a-zA-Z]{2,5}$", "", last)
    return last or path


def _seo(html: str) -> tuple[str, str]:
    """Return (seo_title, meta_description)."""
    title_m = re.search(r"<title>([^<]+)</title>", html, re.IGNORECASE)
    seo_title = html_module.unescape(title_m.group(1).strip()) if title_m else ""
    desc_m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
    meta_desc = html_module.unescape(desc_m.group(1).strip()) if desc_m else ""
    return seo_title, meta_desc


def _reading_time(body_html: str) -> int:
    return max(1, round(len(re.findall(r"\w+", strip_tags(body_html))) / 238))


def _excerpt(body_html: str, fallback: str = "") -> str:
    m = re.search(r"<p[^>]*>(.*?)</p>", body_html, re.DOTALL | re.IGNORECASE)
    return strip_tags(m.group(1))[:400].strip() if m else fallback


# ---------------------------------------------------------------------------
# Site-specific parsers
# ---------------------------------------------------------------------------

def _parse_gc_rpm(html: str, url: str) -> Optional[dict]:
    """GradeCrest / ResearchPaperMate: content in section.page_content."""
    slug = _slug_from_url(url)
    seo_title, meta_desc = _seo(html)

    h1_m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
    title = html_module.unescape(strip_tags(h1_m.group(1))) if h1_m else seo_title

    body_m = re.search(
        r'<section\s+class=["\']page_content["\'][^>]*>(.*?)</section>',
        html, re.IGNORECASE | re.DOTALL,
    )
    if not body_m:
        return None

    body_html = body_m.group(1).strip()
    return {
        "slug": slug, "title": title,
        "seo_title": seo_title, "search_description": meta_desc,
        "hero_headline": title,
        "excerpt": _excerpt(body_html, meta_desc),
        "body_html": body_html,
        "reading_time": _reading_time(body_html),
    }


def _parse_nmg(html: str, url: str) -> Optional[dict]:
    """NurseMyGrade: content in section.blog_body > div.blog_content."""
    slug = _slug_from_url(url)
    seo_title, meta_desc = _seo(html)

    h1_m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
    title = html_module.unescape(strip_tags(h1_m.group(1))) if h1_m else seo_title

    # Try blog_content div inside blog_body first (same as blog pages)
    body_m = re.search(
        r'<div\s+class=["\']blog_content["\'][^>]*>(.*?)</section',
        html, re.IGNORECASE | re.DOTALL,
    )
    if not body_m:
        # Fallback: entire blog_body section
        body_m = re.search(
            r'<section\s+class=["\']blog_body["\'][^>]*>(.*?)</section>',
            html, re.IGNORECASE | re.DOTALL,
        )
    if not body_m:
        return None

    body_html = body_m.group(1).strip()
    # Strip "Related Articles" block that appears at the end
    body_html = re.sub(
        r'<section\s+class=["\']related_sec["\'][^>]*>.*',
        "", body_html, flags=re.IGNORECASE | re.DOTALL,
    ).strip()

    return {
        "slug": slug, "title": title,
        "seo_title": seo_title, "search_description": meta_desc,
        "hero_headline": title,
        "excerpt": _excerpt(body_html, meta_desc),
        "body_html": body_html,
        "reading_time": _reading_time(body_html),
    }


def _parse_em(html: str, url: str) -> Optional[dict]:
    """EssayManiacs: content in section.page_conts."""
    slug = _slug_from_url(url)
    seo_title, meta_desc = _seo(html)

    h1_m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
    title = html_module.unescape(strip_tags(h1_m.group(1))) if h1_m else seo_title

    body_m = re.search(
        r'<section\s+class=["\'][^"\']*page_conts[^"\']*["\'][^>]*>(.*?)</section>',
        html, re.IGNORECASE | re.DOTALL,
    )
    if not body_m:
        return None

    body_html = body_m.group(1).strip()
    # Strip any commented-out HTML at the top
    body_html = re.sub(r'<!--.*?-->', "", body_html, flags=re.DOTALL).strip()

    return {
        "slug": slug, "title": title,
        "seo_title": seo_title, "search_description": meta_desc,
        "hero_headline": title,
        "excerpt": _excerpt(body_html, meta_desc),
        "body_html": body_html,
        "reading_time": _reading_time(body_html),
    }


PARSERS = {
    "gc_rpm": _parse_gc_rpm,
    "nmg":    _parse_nmg,
    "em":     _parse_em,
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Scrape live service pages and output import-ready JSON.")
    ap.add_argument("--site",   required=True)
    ap.add_argument("--out",    required=True)
    ap.add_argument("--limit",  type=int, default=0)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--delay",  type=float, default=0.6)
    args = ap.parse_args()

    site = args.site.lower().strip()
    if site not in SITE_PROFILES:
        sys.exit(f"Unknown site '{site}'. Known: {', '.join(SITE_PROFILES)}")

    profile    = SITE_PROFILES[site]
    parse_fn   = PARSERS[profile["parser"]]
    skip_paths = {p.rstrip("/") for p in profile.get("skip_paths", set())}

    existing: dict[str, dict] = {}
    if args.resume and os.path.exists(args.out):
        with open(args.out, encoding="utf-8") as f:
            for item in json.load(f):
                existing[item["slug"]] = item
        print(f"Resuming — {len(existing)} already in output.")

    print(f"Fetching sitemap: {profile['sitemap_url']}")
    all_urls = _fetch_sitemap_urls(profile["sitemap_url"])
    urls = [u for u in all_urls if urlparse(u).path.rstrip("/") not in skip_paths]
    if len(urls) != len(all_urls):
        print(f"Skipped {len(all_urls) - len(urls)} non-content URLs.")
    print(f"Found {len(urls)} service page URLs.")

    if args.limit:
        urls = urls[:args.limit]

    results: list[dict] = list(existing.values())
    done = errors = skipped = 0

    for i, url in enumerate(urls, 1):
        slug = _slug_from_url(url)
        if slug in existing:
            skipped += 1
            continue

        print(f"  [{i}/{len(urls)}] {slug}", end="", flush=True)
        try:
            html = _fetch(url)
            article = parse_fn(html, url)
            if article and article.get("body_html"):
                results.append(article)
                done += 1
                print(f" ✓ ({article['reading_time']}min, {len(article['body_html'])} chars)")
            else:
                print(" SKIP (no content found)")
                skipped += 1
        except Exception as exc:
            print(f" ERROR: {exc}")
            errors += 1

        if done % 10 == 0 and done > 0:
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

        time.sleep(args.delay)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nDone. Scraped={done} Skipped={skipped} Errors={errors} → {args.out}")
    print(f"\nNext step:")
    print(f"  docker compose cp {args.out} web:{args.out}")
    print(f"  docker compose exec web python manage.py import_service_pages \\")
    print(f"      --site {site} --file {args.out}")


if __name__ == "__main__":
    main()
