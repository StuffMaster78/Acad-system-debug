from __future__ import annotations


def generate_preview_metadata(url: str) -> dict | None:
    """
    Fetch Open Graph / meta tags for a URL and return a preview dict.
    Returns None on any failure so callers can treat it as a no-op.
    """
    try:
        import urllib.request
        from html.parser import HTMLParser

        class _MetaParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.meta: dict[str, str] = {}
                self.title: str = ""
                self._in_title = False

            def handle_starttag(self, tag, attrs):
                attrs_dict = dict(attrs)
                if tag == "title":
                    self._in_title = True
                if tag == "meta":
                    prop = attrs_dict.get("property") or attrs_dict.get("name", "")
                    content = attrs_dict.get("content", "")
                    if prop and content:
                        self.meta[prop] = content

            def handle_endtag(self, tag):
                if tag == "title":
                    self._in_title = False

            def handle_data(self, data):
                if self._in_title and not self.title:
                    self.title = data.strip()

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; LinkPreviewBot/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                return None
            html = resp.read(65536).decode("utf-8", errors="replace")

        parser = _MetaParser()
        parser.feed(html)

        title = (
            parser.meta.get("og:title")
            or parser.meta.get("twitter:title")
            or parser.title
            or ""
        )
        description = (
            parser.meta.get("og:description")
            or parser.meta.get("description")
            or ""
        )
        image = parser.meta.get("og:image") or parser.meta.get("twitter:image") or ""

        if not title:
            return None

        return {
            "url": url,
            "title": title[:200],
            "description": description[:500],
            "image": image,
        }

    except Exception:
        return None
