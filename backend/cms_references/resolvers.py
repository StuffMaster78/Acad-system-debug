"""
Reference Resolution Services
===============================

DOIResolver: paste a DOI, get full bibliographic metadata from Crossref.
PMIDResolver: paste a PubMed ID, get metadata from NCBI eutils.
LinkRotChecker: weekly verification of reference URLs.
WaybackArchiver: archive URLs via web.archive.org on first add.
"""

import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

CROSSREF_API = "https://api.crossref.org/works"
NCBI_ESUMMARY_API = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
WAYBACK_SAVE_API = "https://web.archive.org/save"

REQUEST_TIMEOUT = 10 # seconds


class DOIResolver:
    """Resolve a DOI to full bibliographic metadata via Crossref API (free, no auth)."""

    @staticmethod
    def resolve(doi: str) -> Optional[dict]:
        """Given a DOI string, return a dict of reference fields or None on failure."""
        doi = doi.strip().removeprefix("https://doi.org/").removeprefix("http://doi.org/")
        url = f"{CROSSREF_API}/{doi}"

        try:
            response = requests.get(
                url,
                headers={"Accept": "application/json"},
                timeout=REQUEST_TIMEOUT,
            )
            if response.status_code != 200:
                logger.warning("DOI resolution failed for %s: HTTP %s", doi, response.status_code)
                return None

            data = response.json().get("message", {})

            authors = []
            for author in data.get("author", []):
                authors.append({
                    "family": author.get("family", ""),
                    "given": author.get("given", ""),
                })

            # Extract year from date-parts
            year = None
            date_parts = data.get("published-print", data.get("published-online", {}))
            if date_parts and date_parts.get("date-parts"):
                parts = date_parts["date-parts"][0]
                if parts:
                    year = parts[0]

            return {
                "title": " ".join(data.get("title", [])),
                "authors": authors,
                "publication_year": year,
                "journal_name": " ".join(data.get("container-title", [])),
                "journal_volume": data.get("volume", ""),
                "journal_issue": data.get("issue", ""),
                "pages": data.get("page", ""),
                "publisher": data.get("publisher", ""),
                "doi": doi,
                "issn": (data.get("ISSN", [""]))[0] if data.get("ISSN") else "",
                "url": data.get("URL", ""),
                "is_peer_reviewed": True,
                "reference_type": "journal_article",
            }

        except requests.RequestException as e:
            logger.error("DOI resolution error for %s: %s", doi, e)
            return None


class PMIDResolver:
    """Resolve a PubMed ID to bibliographic metadata via NCBI eutils."""

    @staticmethod
    def resolve(pmid: str) -> Optional[dict]:
        """Given a PMID string, return a dict of reference fields or None."""
        pmid = pmid.strip()

        try:
            response = requests.get(
                NCBI_ESUMMARY_API,
                params={
                    "db": "pubmed",
                    "id": pmid,
                    "retmode": "json",
                },
                timeout=REQUEST_TIMEOUT,
            )
            if response.status_code != 200:
                logger.warning("PMID resolution failed for %s: HTTP %s", pmid, response.status_code)
                return None

            data = response.json()
            result = data.get("result", {}).get(pmid, {})

            if not result or "error" in result:
                logger.warning("PMID not found: %s", pmid)
                return None

            authors = []
            for author in result.get("authors", []):
                name_parts = author.get("name", "").split(" ", 1)
                authors.append({
                    "family": name_parts[0] if name_parts else "",
                    "given": name_parts[1] if len(name_parts) > 1 else "",
                })

            # Extract year from pubdate
            pub_date = result.get("pubdate", "")
            year = None
            if pub_date:
                try:
                    year = int(pub_date.split(" ")[0])
                except (ValueError, IndexError):
                    pass

            return {
                "title": result.get("title", ""),
                "authors": authors,
                "publication_year": year,
                "journal_name": result.get("fulljournalname", result.get("source", "")),
                "journal_volume": result.get("volume", ""),
                "journal_issue": result.get("issue", ""),
                "pages": result.get("pages", ""),
                "pmid": pmid,
                "doi": next(
                    (
                        aid.get("value", "")
                        for aid in result.get("articleids", [])
                        if aid.get("idtype") == "doi"
                    ),
                    "",
                ),
                "is_peer_reviewed": True,
                "reference_type": "journal_article",
            }

        except requests.RequestException as e:
            logger.error("PMID resolution error for %s: %s", pmid, e)
            return None


class LinkRotChecker:
    """Check if a URL is still reachable.
    Called by a weekly Celery task."""

    @staticmethod
    def check_url(url: str) -> dict:
        """HEAD request to URL. Returns status dict."""
        try:
            response = requests.head(
                url,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True,
                headers={"User-Agent": "CMS-LinkChecker/1.0"},
            )
            return {
                "reachable": response.status_code == 200,
                "status_code": response.status_code,
                "final_url": response.url,
            }
        except requests.RequestException as e:
            return {
                "reachable": False,
                "status_code": None,
                "error": str(e),
            }


class WaybackArchiver:
    """Archive a URL via the Wayback Machine.
    Called on first add of a Reference with a URL."""

    @staticmethod
    def archive(url: str) -> Optional[str]:
        """Submit URL to Wayback Machine. Returns archived URL or None."""
        try:
            response = requests.get(
                f"{WAYBACK_SAVE_API}/{url}",
                timeout=30, # Wayback can be slow
                headers={"User-Agent": "CMS-Archiver/1.0"},
            )

            # The Wayback Machine returns the archived URL in
            # the Content-Location or Link header
            archived_url = response.headers.get("Content-Location", "")
            if archived_url:
                return f"https://web.archive.org{archived_url}"

            # Fallback: construct from the URL pattern
            if response.status_code == 200:
                return f"https://web.archive.org/web/{url}"

            logger.warning("Wayback archiving failed for %s: HTTP %s", url, response.status_code)
            return None

        except requests.RequestException as e:
            logger.error("Wayback archiving error for %s: %s", url, e)
            return None