#!/usr/bin/env python3
"""
fix_scraped_content.py
======================
Post-processes scraped JSON files (from scrape_live_services.py or
scrape_live_blog.py) to:

  1. Download all <img> src images to a local media directory
     and rewrite src attributes to point to the local copy.

  2. Convert internal links (absolute URLs pointing to the same site)
     to relative paths so they work in the new system without depending
     on the live site.

Writes a new JSON file (--out) with updated body_html values, safe to then
import with import_blog_posts or import_service_pages.

Usage:
    python3 scripts/fix_scraped_content.py \\
        --site gradecrest.com \\
        --in /tmp/gc_services.json \\
        --out /tmp/gc_services_fixed.json \\
        --media-dir /tmp/scraped_media/gradecrest

    python3 scripts/fix_scraped_content.py \\
        --site nursemygrade.com \\
        --in /tmp/nmg_articles.json \\
        --out /tmp/nmg_articles_fixed.json \\
        --media-dir /tmp/scraped_media/nursemygrade \\
        --links-only   # skip image download, just fix links
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fetch_image(url: str, dest_dir: Path, retries: int = 3) -> str | None:
    """Download image URL to dest_dir. Returns the local filename or None on failure."""
    parsed = urlparse(url)
    ext = Path(parsed.path).suffix.lower() or '.jpg'
    if ext not in {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.avif'}:
        ext = '.jpg'

    # Stable filename based on URL hash so re-runs don't re-download
    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    orig_stem = Path(parsed.path).stem[:40].replace(' ', '_')
    filename = f"{orig_stem}_{url_hash}{ext}"
    dest = dest_dir / filename

    if dest.exists():
        return filename  # already downloaded

    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; ContentFixer/1.0)',
        'Accept': 'image/*,*/*;q=0.8',
    }
    req = urllib.request.Request(url, headers=headers)

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                dest.write_bytes(resp.read())
            return filename
        except Exception:
            if attempt == retries - 1:
                return None
            time.sleep(2 ** attempt)
    return None


def fix_images(html: str, site: str, media_dir: Path, media_url_prefix: str, delay: float) -> tuple[str, int, int]:
    """
    Find all <img> tags in html, download each image, rewrite src.
    Returns (updated_html, downloaded_count, failed_count).
    """
    downloaded = failed = 0

    def replace_img(m: re.Match) -> str:
        nonlocal downloaded, failed
        tag = m.group(0)
        src_m = re.search(r'\bsrc=["\']([^"\']+)["\']', tag, re.IGNORECASE)
        if not src_m:
            return tag

        src = src_m.group(1)

        # Skip data URIs and already-local paths
        if src.startswith('data:') or src.startswith('/media/') or not src.startswith('http'):
            return tag

        # Only download images from the same site (or any site if cross-domain)
        parsed = urlparse(src)
        if parsed.netloc and parsed.netloc != site and not parsed.netloc.endswith(f'.{site}'):
            return tag  # external image from a different domain — leave as-is

        filename = _fetch_image(src, media_dir, retries=2)
        if filename:
            downloaded += 1
            new_src = f'{media_url_prefix}/{filename}'
            tag = tag[:src_m.start(1)] + new_src + tag[src_m.end(1):]
        else:
            failed += 1

        return tag

    updated = re.sub(r'<img[^>]+>', replace_img, html, flags=re.IGNORECASE)
    return updated, downloaded, failed


def fix_internal_links(html: str, site: str) -> tuple[str, int]:
    """
    Convert absolute internal links to relative paths.
    e.g. https://gradecrest.com/services/essay-writing →  /services/essay-writing
    Returns (updated_html, count_of_links_fixed).
    """
    count = 0
    base_patterns = [
        re.compile(rf'href=["\']https?://{re.escape(site)}(/[^"\']*)["\']', re.IGNORECASE),
        re.compile(rf'href=["\']https?://www\.{re.escape(site)}(/[^"\']*)["\']', re.IGNORECASE),
    ]

    def replace_link(m: re.Match) -> str:
        nonlocal count
        count += 1
        return f'href="{m.group(1)}"'

    for pattern in base_patterns:
        html = pattern.sub(replace_link, html)

    return html, count


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Fix internal links and download images in scraped JSON.")
    ap.add_argument('--site',         required=True,  help='Site domain, e.g. gradecrest.com')
    ap.add_argument('--in',           required=True,  dest='input', help='Input JSON file')
    ap.add_argument('--out',          required=True,  help='Output JSON file')
    ap.add_argument('--media-dir',    default='/tmp/scraped_media', help='Directory to save downloaded images')
    ap.add_argument('--media-prefix', default='/media/scraped', help='URL prefix for rewritten img src attributes')
    ap.add_argument('--links-only',   action='store_true', help='Fix links only, skip image download')
    ap.add_argument('--images-only',  action='store_true', help='Download images only, skip link fixing')
    ap.add_argument('--delay',        type=float, default=0.3, help='Delay between image downloads (seconds)')
    args = ap.parse_args()

    if not os.path.exists(args.input):
        sys.exit(f"Input file not found: {args.input}")

    with open(args.input, encoding='utf-8') as f:
        items = json.load(f)

    if not isinstance(items, list):
        sys.exit("JSON must be a top-level array.")

    print(f"Loaded {len(items)} items from {args.input}")

    media_dir = Path(args.media_dir) / args.site
    media_dir.mkdir(parents=True, exist_ok=True)

    total_links = total_imgs_ok = total_imgs_fail = 0

    for i, item in enumerate(items, 1):
        slug = item.get('slug', f'[{i}]')
        html = item.get('body_html', '') or ''
        if not html:
            continue

        # Fix internal links
        n_links = 0
        if not args.images_only:
            html, n_links = fix_internal_links(html, args.site)
            total_links += n_links

        # Download and rewrite images
        if not args.links_only:
            html, n_ok, n_fail = fix_images(
                html, args.site, media_dir, args.media_prefix, args.delay
            )
            total_imgs_ok   += n_ok
            total_imgs_fail += n_fail
            if n_ok or n_fail:
                print(f"  [{i}/{len(items)}] {slug} — links:{n_links} imgs:✓{n_ok}/✗{n_fail}")
                time.sleep(args.delay)
        else:
            if n_links:
                print(f"  [{i}/{len(items)}] {slug} — {n_links} links fixed")

        item['body_html'] = html

    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"\nDone.")
    print(f"  Links fixed:     {total_links}")
    print(f"  Images saved:    {total_imgs_ok}  →  {media_dir}")
    print(f"  Images failed:   {total_imgs_fail}")
    print(f"  Output:          {args.out}")

    if total_imgs_ok:
        print(f"\nNext step — copy images into Django media:")
        print(f"  docker compose cp {media_dir} web:/app/media/scraped/{args.site}")

    print(f"\nThen re-import with --update flag:")
    print(f"  docker compose exec web python manage.py import_service_pages \\")
    print(f"      --site {args.site} --file {args.out} --update")


if __name__ == '__main__':
    main()
