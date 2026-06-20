#!/usr/bin/env python3
"""
scrape_live_blog.py
===================
Scrapes blog posts from a live website and writes them as a JSON file
compatible with the import_blog_posts management command.

Reads post URLs from the site's XML sitemap (or a sitemap index), fetches
each page, and extracts content using site-specific CSS selectors.

Supported sites (built-in profiles):
  gradecrest.com  — <section class="blog_content"> layout

Usage:
    python3 scripts/scrape_live_blog.py \\
        --site gradecrest.com \\
        --out /tmp/gradecrest_articles.json

    # Limit to first 10 posts (for testing):
    python3 scripts/scrape_live_blog.py \\
        --site gradecrest.com \\
        --out /tmp/gc_test.json \\
        --limit 10

    # Resume after a partial run (skip slugs already in output file):
    python3 scripts/scrape_live_blog.py \\
        --site gradecrest.com \\
        --out /tmp/gradecrest_articles.json \\
        --resume

Then import with:
    docker compose cp /tmp/gradecrest_articles.json web:/tmp/gradecrest_articles.json
    docker compose exec web python manage.py import_blog_posts \\
        --site gradecrest.com \\
        --file /tmp/gradecrest_articles.json

Re-run with --update to refresh body/excerpt on already-imported posts.

Dependencies (stdlib only — no BeautifulSoup needed):
    Python 3.8+, urllib.request, xml.etree.ElementTree, html.parser
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
        "sitemap_url": "https://gradecrest.com/blogs-sitemap.xml",
        "base_url": "https://gradecrest.com",
        "parser": "gradecrest",
    },
    "nursemygrade.com": {
        "sitemap_url": "https://nursemygrade.com/sitemap-blogs.xml",
        "base_url": "https://nursemygrade.com",
        "parser": "nursemygrade",
        # skip the blog index page listed in the sitemap
        "skip_paths": {"/blog", "/blog/"},
    },
    "researchpapermate.com": {
        "sitemap_url": "https://researchpapermate.com/blogs-sitemap.xml",
        "base_url": "https://researchpapermate.com",
        "parser": "researchpapermate",   # same layout as gradecrest
    },
    "essaymaniacs.com": {
        "sitemap_url": "https://essaymaniacs.com/sitemap-blogs.xml",
        "base_url": "https://essaymaniacs.com",
        "parser": "essaymaniacs",
        "skip_paths": {"/blog", "/blog/"},
    },
}


# ---------------------------------------------------------------------------
# Minimal HTML utilities (stdlib only)
# ---------------------------------------------------------------------------

class _TextExtractor(HTMLParser):
    """Strip tags and return plain text."""
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
            "Mozilla/5.0 (compatible; BlogImporter/1.0; "
            "+https://github.com/your-org/writing-system)"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
                # detect encoding from Content-Type or <meta charset>
                ct = resp.headers.get("Content-Type", "")
                enc = "utf-8"
                m = re.search(r"charset=([^\s;]+)", ct)
                if m:
                    enc = m.group(1).strip()
                return raw.decode(enc, errors="replace")
        except Exception as exc:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)
    return ""


def _fetch_sitemap_urls(sitemap_url: str) -> list[str]:
    """Return all <loc> URLs from a sitemap or sitemap index."""
    xml = _fetch(sitemap_url)
    # Strip all namespace declarations and prefixes so ET can parse without registration
    xml = re.sub(r'\s+xmlns(?::\w+)?="[^"]*"', "", xml)   # remove xmlns attrs
    xml = re.sub(r'\s+xsi:[a-zA-Z]+="[^"]*"', "", xml)    # remove xsi:* attrs
    xml = re.sub(r'<(\w+):', "<", xml)                     # strip element prefixes
    xml = re.sub(r'</(\w+):', "</", xml)                   # strip closing prefixes
    xml = re.sub(r'<\?xml-stylesheet[^?]*\?>', "", xml)    # strip processing instructions
    root = ET.fromstring(xml)

    urls: list[str] = []
    # sitemap index → recurse
    for sm in root.findall(".//sitemap/loc"):
        urls.extend(_fetch_sitemap_urls(sm.text.strip()))
    # regular sitemap
    for loc in root.findall(".//url/loc"):
        urls.append(loc.text.strip())

    return urls


# ---------------------------------------------------------------------------
# Page parsers
# ---------------------------------------------------------------------------

def _parse_gradecrest(html: str, url: str) -> Optional[dict]:
    """
    Extract article data from a GradeCrest blog post page.

    Structure:
      <section class="blog_content">
        <h1>…</h1>
        <div class="mod_time">…Last Updated: DD Month YYYY | Author: <a href="/author/slug/">Name</a></div>
        <img …>
        <p>…</p>
        …
      </section>
    """
    slug = urlparse(url).path.strip("/").split("/")[-1]
    if not slug:
        return None

    # --- SEO fields from <head> -----------------------------------------
    seo_title_m = re.search(r"<title>([^<]+)</title>", html, re.IGNORECASE)
    seo_title = html_module.unescape(seo_title_m.group(1).strip()) if seo_title_m else ""

    meta_desc_m = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
        html, re.IGNORECASE,
    )
    if not meta_desc_m:
        meta_desc_m = re.search(
            r'<meta\s+content=["\'](.*?)["\']\s+name=["\']description["\']',
            html, re.IGNORECASE,
        )
    meta_desc = html_module.unescape(meta_desc_m.group(1).strip()) if meta_desc_m else ""

    # --- Content section ------------------------------------------------
    section_m = re.search(
        r'<section\s+class=["\']blog_content["\'][^>]*>(.*?)</section>',
        html, re.IGNORECASE | re.DOTALL,
    )
    if not section_m:
        print(f"  WARN: no blog_content section found at {url}", file=sys.stderr)
        return None

    section_html = section_m.group(1)

    # h1 title
    h1_m = re.search(r"<h1[^>]*>(.*?)</h1>", section_html, re.IGNORECASE | re.DOTALL)
    title = html_module.unescape(strip_tags(h1_m.group(1))) if h1_m else seo_title

    # mod_time div → date + author
    mod_time_m = re.search(
        r'<div\s+class=["\']mod_time["\'][^>]*>(.*?)</div>',
        section_html, re.IGNORECASE | re.DOTALL,
    )
    published_at = ""
    author_name = ""
    author_slug = ""

    if mod_time_m:
        mod_html = mod_time_m.group(1)

        date_m = re.search(
            r"(?:Last Updated|Published)[:\s]+(\d{1,2}\s+\w+\s+\d{4})",
            mod_html, re.IGNORECASE,
        )
        if date_m:
            raw_date = date_m.group(1).strip()
            try:
                from datetime import datetime
                published_at = datetime.strptime(raw_date, "%d %B %Y").strftime("%Y-%m-%d")
            except ValueError:
                published_at = ""

        author_m = re.search(
            r'href=["\'][^"\']*?/author/([^/"\']+)/["\'][^>]*>(.*?)</a>',
            mod_html, re.IGNORECASE | re.DOTALL,
        )
        if author_m:
            author_slug = author_m.group(1).strip()
            author_name = strip_tags(author_m.group(2)).strip()

    # body: everything after the mod_time div and the first <img>
    body_html = section_html

    # strip h1
    body_html = re.sub(r"<h1[^>]*>.*?</h1>", "", body_html, count=1, flags=re.DOTALL | re.IGNORECASE)

    # strip mod_time div
    body_html = re.sub(
        r'<div\s+class=["\']mod_time["\'][^>]*>.*?</div>',
        "", body_html, count=1, flags=re.DOTALL | re.IGNORECASE,
    )

    # strip first <img> (hero image)
    body_html = re.sub(r"<img\b[^>]*/?>", "", body_html, count=1, flags=re.IGNORECASE)

    body_html = body_html.strip()

    # excerpt: plain text of first <p>
    first_p_m = re.search(r"<p[^>]*>(.*?)</p>", body_html, re.DOTALL | re.IGNORECASE)
    excerpt = strip_tags(first_p_m.group(1))[:400].strip() if first_p_m else meta_desc

    # reading time: ~238 words/min
    word_count = len(re.findall(r"\w+", strip_tags(body_html)))
    reading_time = max(1, round(word_count / 238))

    return {
        "slug": slug,
        "title": title,
        "excerpt": excerpt,
        "body_html": body_html,
        "category": "Blog",
        "tags": [],
        "author_name": author_name or "GradeCrest Editorial Team",
        "author_slug": author_slug or "gradecrest-editorial",
        "published_at": published_at,
        "seo_title": seo_title,
        "search_description": meta_desc,
        "reading_time": reading_time,
    }


def _parse_nursemygrade(html: str, url: str) -> Optional[dict]:
    """
    NurseMyGrade layout:
      <div class="blog_top_txt"><h1>…</h1>  <author_name>  <blog_date><span>Month DD, YYYY</span>
      <section class="blog_body"><div class="blog_content">…</div></section>
    """
    slug = urlparse(url).path.strip("/").split("/")[-1]
    if not slug:
        return None

    seo_title_m = re.search(r"<title>([^<]+)</title>", html, re.IGNORECASE)
    seo_title = html_module.unescape(seo_title_m.group(1).strip()) if seo_title_m else ""

    meta_desc_m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
    meta_desc = html_module.unescape(meta_desc_m.group(1).strip()) if meta_desc_m else ""

    h1_m = re.search(r'<div\s+class=["\']blog_top_txt["\'][^>]*>.*?<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
    title = html_module.unescape(strip_tags(h1_m.group(1))) if h1_m else seo_title

    # Author: <span class="author_name"><span>Written by</span><span>NAME</span></span>
    author_name = ""
    author_slug = ""
    auth_block_m = re.search(r'<span\s+class=["\']author_name["\'][^>]*>(.*?)</span\s*>', html, re.IGNORECASE | re.DOTALL)
    if auth_block_m:
        # strip "Written by" spans, keep the name
        spans = re.findall(r'<span[^>]*>(.*?)</span>', auth_block_m.group(1), re.DOTALL)
        parts = [strip_tags(s).strip().rstrip(".") for s in spans if strip_tags(s).strip() and "written by" not in strip_tags(s).lower()]
        if parts:
            author_name = parts[0]
            author_slug = re.sub(r"[^a-z0-9]+", "-", author_name.lower()).strip("-")

    # Date: <div class="blog_date"><span>Month DD, YYYY</span>
    published_at = ""
    date_m = re.search(r'<div\s+class=["\']blog_date["\'][^>]*>\s*<span>([^<]+)</span>', html, re.IGNORECASE)
    if date_m:
        raw = date_m.group(1).strip()
        try:
            from datetime import datetime
            published_at = datetime.strptime(raw, "%B %d, %Y").strftime("%Y-%m-%d")
        except ValueError:
            published_at = ""

    # Body: content of div.blog_content
    body_m = re.search(r'<div\s+class=["\']blog_content["\'][^>]*>(.*?)</div\s*>\s*</section', html, re.IGNORECASE | re.DOTALL)
    if not body_m:
        body_m = re.search(r'<div\s+class=["\']blog_content["\'][^>]*>(.*?)</section', html, re.IGNORECASE | re.DOTALL)
    if not body_m:
        return None

    body_html = body_m.group(1).strip()
    first_p = re.search(r"<p[^>]*>(.*?)</p>", body_html, re.DOTALL | re.IGNORECASE)
    excerpt = strip_tags(first_p.group(1))[:400].strip() if first_p else meta_desc
    reading_time = max(1, round(len(re.findall(r"\w+", strip_tags(body_html))) / 238))

    return {
        "slug": slug, "title": title, "excerpt": excerpt, "body_html": body_html,
        "category": "Blog", "tags": [],
        "author_name": author_name or "NurseMyGrade Editorial Team",
        "author_slug": author_slug or "nursemygrade-editorial",
        "published_at": published_at,
        "seo_title": seo_title, "search_description": meta_desc, "reading_time": reading_time,
    }


def _parse_researchpapermate(html: str, url: str) -> Optional[dict]:
    """Same layout as GradeCrest (section.blog_content + mod_time div)."""
    return _parse_gradecrest(html, url)


def _parse_essaymaniacs(html: str, url: str) -> Optional[dict]:
    """
    EssayManiacs layout:
      <div class="blog_titles"><div class="blog_header"><h1 class="white">…</h1>
        <span class="author_name">By NAME</span>
      <section class="company_content blog_cont">…</section>
    """
    slug = urlparse(url).path.strip("/").split("/")[-1]
    if not slug:
        return None

    seo_title_m = re.search(r"<title>([^<]+)</title>", html, re.IGNORECASE)
    seo_title = html_module.unescape(seo_title_m.group(1).strip()) if seo_title_m else ""

    meta_desc_m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
    meta_desc = html_module.unescape(meta_desc_m.group(1).strip()) if meta_desc_m else ""

    h1_m = re.search(r'<h1[^>]*class=["\'][^"\']*white[^"\']*["\'][^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
    title = html_module.unescape(strip_tags(h1_m.group(1))) if h1_m else seo_title

    # Author: <span class="author_name">By NAME</span>
    author_name = ""
    author_slug = ""
    auth_m = re.search(r'<span\s+class=["\']author_name["\'][^>]*>(.*?)</span>', html, re.IGNORECASE | re.DOTALL)
    if auth_m:
        raw = strip_tags(auth_m.group(1)).strip()
        name = re.sub(r"^by\s+", "", raw, flags=re.IGNORECASE).strip()
        if name:
            author_name = name
            author_slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

    # Body: section.company_content.blog_cont
    body_m = re.search(
        r'<section\s+class=["\'][^"\']*company_content[^"\']*blog_cont[^"\']*["\'][^>]*>(.*?)</section>',
        html, re.IGNORECASE | re.DOTALL,
    )
    if not body_m:
        body_m = re.search(
            r'<section\s+class=["\'][^"\']*blog_cont[^"\']*["\'][^>]*>(.*?)</section>',
            html, re.IGNORECASE | re.DOTALL,
        )
    if not body_m:
        return None

    body_html = body_m.group(1).strip()
    first_p = re.search(r"<p[^>]*>(.*?)</p>", body_html, re.DOTALL | re.IGNORECASE)
    excerpt = strip_tags(first_p.group(1))[:400].strip() if first_p else meta_desc
    reading_time = max(1, round(len(re.findall(r"\w+", strip_tags(body_html))) / 238))

    return {
        "slug": slug, "title": title, "excerpt": excerpt, "body_html": body_html,
        "category": "Blog", "tags": [],
        "author_name": author_name or "EssayManiacs Editorial Team",
        "author_slug": author_slug or "essaymaniacs-editorial",
        "published_at": "",
        "seo_title": seo_title, "search_description": meta_desc, "reading_time": reading_time,
    }


PARSERS = {
    "gradecrest.com": _parse_gradecrest,
    "nursemygrade.com": _parse_nursemygrade,
    "researchpapermate.com": _parse_researchpapermate,
    "essaymaniacs.com": _parse_essaymaniacs,
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape a live blog and output import-ready JSON.")
    parser.add_argument("--site", required=True, help="Site domain key (e.g. gradecrest.com)")
    parser.add_argument("--out", required=True, help="Output JSON file path")
    parser.add_argument("--limit", type=int, default=0, help="Max posts to fetch (0 = all)")
    parser.add_argument("--resume", action="store_true", help="Skip slugs already present in --out")
    parser.add_argument("--delay", type=float, default=0.8, help="Seconds between requests (default 0.8)")
    args = parser.parse_args()

    site = args.site.lower().strip()
    if site not in SITE_PROFILES:
        sys.exit(f"ERROR: unknown site '{site}'. Known: {', '.join(SITE_PROFILES)}")

    profile  = SITE_PROFILES[site]
    parse_fn = PARSERS[site]
    skip_paths = profile.get("skip_paths", set())

    # Resume: load existing output
    existing: dict[str, dict] = {}
    if args.resume and os.path.exists(args.out):
        with open(args.out, encoding="utf-8") as f:
            for item in json.load(f):
                existing[item["slug"]] = item
        print(f"Resuming: {len(existing)} posts already in output file.")

    # Fetch sitemap
    print(f"Fetching sitemap: {profile['sitemap_url']}")
    all_urls = _fetch_sitemap_urls(profile["sitemap_url"])
    # Filter out index/non-article paths (e.g. /blog, /blog/)
    urls = [u for u in all_urls if urlparse(u).path.rstrip("/") not in {p.rstrip("/") for p in skip_paths}]
    if len(urls) != len(all_urls):
        print(f"Skipped {len(all_urls) - len(urls)} non-article URLs (index pages).")
    print(f"Found {len(urls)} article URLs.")

    if args.limit:
        urls = urls[: args.limit]
        print(f"Limiting to {args.limit} posts.")

    results: list[dict] = list(existing.values())
    done = 0
    skipped = 0
    errors = 0

    for i, url in enumerate(urls, 1):
        slug = urlparse(url).path.strip("/").split("/")[-1]

        if slug in existing:
            skipped += 1
            continue

        print(f"  [{i}/{len(urls)}] {slug}", end="", flush=True)
        try:
            html = _fetch(url)
            article = parse_fn(html, url)
            if article:
                results.append(article)
                done += 1
                print(f" ✓ ({article['reading_time']}min)")
            else:
                print(" SKIP (no content found)")
                skipped += 1
        except Exception as exc:
            print(f" ERROR: {exc}")
            errors += 1

        # Write incrementally so a crash doesn't lose progress
        if done % 10 == 0 and done > 0:
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

        time.sleep(args.delay)

    # Final write
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nDone. Scraped={done} Skipped={skipped} Errors={errors} → {args.out}")
    print(f"\nNext step:")
    print(f"  docker compose cp {args.out} web:{args.out}")
    print(f"  docker compose exec web python manage.py import_blog_posts \\")
    print(f"      --site {site} \\")
    print(f"      --file {args.out}")


if __name__ == "__main__":
    main()
