#!/usr/bin/env python3
"""
export_static_blog_to_json.py
==============================
Reads the static blog posts from a site's useBlog.ts composable (TypeScript)
and writes them as a JSON file compatible with the import_blog_posts management
command.

Works by extracting structured data from the TypeScript source using a
simple regex approach — not a full TS parser, but good enough for the
structured blog post arrays used in this project.

Usage:
    python3 scripts/export_static_blog_to_json.py \\
        --site nursemygrade-web \\
        --out /tmp/nursemygrade_articles.json

    python3 scripts/export_static_blog_to_json.py \\
        --site gradecrest-web \\
        --out /tmp/gradecrest_articles.json

Then import with:
    docker compose exec web python manage.py import_blog_posts \\
        --site nursemygrade.com \\
        --file /tmp/nursemygrade_articles.json

Alternative (from WordPress or other CMS):
    See --help for the JSON schema required.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

SITE_DEFAULTS = {
    "nursemygrade-web": {
        "site_domain": "nursemygrade.com",
        "author_name": "NurseMyGrade Editorial Team",
        "author_slug": "nursemygrade-editorial",
        "author_credentials": "BSN · MSN · DNP Nurse Writers",
        "author_bio": "Expert nurse writers with active clinical experience.",
    },
    "gradecrest-web": {
        "site_domain": "gradecrest.com",
        "author_name": "GradeCrest Editorial Team",
        "author_slug": "gradecrest-editorial",
        "author_credentials": "PhD · MA · BA Academic Writers",
        "author_bio": "GradeCrest academic writing experts.",
    },
    "essaymaniacs-web": {
        "site_domain": "essaymaniacs.com",
        "author_name": "EssayManiacs Editorial Team",
        "author_slug": "essaymaniacs-editorial",
        "author_credentials": "MA · BA Academic Writers",
        "author_bio": "EssayManiacs expert writing team.",
    },
    "researchpapermate-web": {
        "site_domain": "researchpapermate.com",
        "author_name": "ResearchPaperMate Editorial Team",
        "author_slug": "researchpapermate-editorial",
        "author_credentials": "PhD · MA Research Writers",
        "author_bio": "ResearchPaperMate research writing specialists.",
    },
}


def extract_posts_from_ts(ts_source: str, defaults: dict) -> list[dict]:
    """
    Extract blog posts from a useBlog.ts source string.

    The TypeScript file defines a `posts: BlogPost[]` array with object
    literals. We use regex to pull out the key string fields and the
    body HTML (body: `...`) for each post.

    This is intentionally simple — it handles the specific structure used
    in this project's useBlog.ts files.
    """

    # Find all post objects within the array literal
    # Strategy: split on `  {` at top-level then parse each chunk
    articles = []

    # Extract slug, title, excerpt, date, category, and body for each post
    # We look for the BlogPost interface fields
    slug_re    = re.compile(r"slug:\s*'([^']*)'")
    title_re   = re.compile(r"title:\s*'([^']*)'")
    excerpt_re = re.compile(r"excerpt:\s*'([^']*)'")
    date_re    = re.compile(r"\bdate:\s*'([^']*)'")
    category_re= re.compile(r"category:\s*'([^']*)'")
    readtime_re= re.compile(r"readTime:\s*'([^']*)'")

    # Body is a template literal: body: `...`
    body_re    = re.compile(r"body:\s*`([\s\S]*?)`", re.DOTALL)

    # Author block (if present)
    author_name_re  = re.compile(r"name:\s*'([^']*)'")
    author_creds_re = re.compile(r"credentials:\s*'([^']*)'")
    author_bio_re_m = re.compile(r"bio:\s*'([\s\S]*?)'")

    # Simple split: find each post object block starting with `slug:`
    # We split on `\n  {\n` boundaries
    # Better: find all top-level {...} blocks in the const posts array

    # Locate the `const posts: BlogPost[] = [` array
    array_match = re.search(r'const posts[^=]*=\s*\[', ts_source)
    if not array_match:
        return []

    array_start = array_match.end()

    # Walk through braces to find each post object
    depth = 0
    current_start = None
    blocks = []
    i = array_start
    in_template = False
    template_char = None

    while i < len(ts_source):
        c = ts_source[i]

        # Handle template literals
        if c == '`' and not in_template:
            in_template = True
            template_char = c
            i += 1
            continue
        if in_template and c == '`':
            in_template = False
            i += 1
            continue
        if in_template:
            i += 1
            continue

        if c == '{':
            if depth == 0:
                current_start = i
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0 and current_start is not None:
                blocks.append(ts_source[current_start:i+1])
                current_start = None
        elif c == ']' and depth == 0:
            break  # end of posts array

        i += 1

    for block in blocks:
        slug_m    = slug_re.search(block)
        title_m   = title_re.search(block)
        excerpt_m = excerpt_re.search(block)
        date_m    = date_re.search(block)
        cat_m     = category_re.search(block)
        rt_m      = readtime_re.search(block)
        body_m    = body_re.search(block)

        if not (slug_m and title_m):
            continue  # skip malformed blocks

        slug    = slug_m.group(1)
        title   = title_m.group(1)
        excerpt = excerpt_m.group(1) if excerpt_m else ""
        date    = date_m.group(1) if date_m else ""
        category= cat_m.group(1) if cat_m else ""
        readtime_str = rt_m.group(1) if rt_m else "8"
        body_html= body_m.group(1).strip() if body_m else ""

        # Parse reading time (e.g. "12 min read" → 12)
        rt_digits = re.search(r'\d+', readtime_str)
        reading_time = int(rt_digits.group()) if rt_digits else 8

        article = {
            "slug": slug,
            "title": title,
            "excerpt": excerpt,
            "body_html": body_html,
            "category": category,
            "tags": [],
            "author_name": defaults.get("author_name", ""),
            "author_slug": defaults.get("author_slug", "editorial-team"),
            "author_credentials": defaults.get("author_credentials", ""),
            "author_bio": defaults.get("author_bio", ""),
            "published_at": date,
            "reading_time": reading_time,
            "seo_title": title,
            "search_description": excerpt[:255],
        }
        articles.append(article)

    return articles


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--site", required=True, choices=list(SITE_DEFAULTS.keys()),
                        help="Which site's useBlog.ts to read.")
    parser.add_argument("--out", required=True, help="Output JSON file path.")
    parser.add_argument("--ts-file", default=None,
                        help="Custom path to useBlog.ts (auto-detected from --site if omitted).")
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    ts_file = args.ts_file or (repo_root / args.site / "composables" / "useBlog.ts")

    if not ts_file.exists():
        print(f"ERROR: {ts_file} not found.", file=sys.stderr)
        sys.exit(1)

    defaults = SITE_DEFAULTS[args.site]
    ts_source = ts_file.read_text(encoding="utf-8")
    articles = extract_posts_from_ts(ts_source, defaults)

    if not articles:
        print("WARNING: No articles extracted. Check the useBlog.ts format.", file=sys.stderr)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(articles)} articles → {out_path}")
    print(f"Site domain: {defaults['site_domain']}")
    print(f"\nNext step:")
    print(f"  docker compose exec web python manage.py import_blog_posts \\")
    print(f"      --site {defaults['site_domain']} \\")
    print(f"      --file {out_path.absolute()}")


if __name__ == "__main__":
    main()
