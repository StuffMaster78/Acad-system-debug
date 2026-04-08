import logging
from typing import Dict, Optional

import requests
from django.core.cache import cache
from django.conf import settings


logger = logging.getLogger(__name__)


class GeoService:
    """
    Resolve IP address to geographic and network information.
    """

    CACHE_TIMEOUT = 60 * 60 * 24  # 24 hours

    @classmethod
    def get_geo(cls, ip: str) -> Dict[str, Optional[str]]:
        """
        Resolve IP to geo data with caching.

        Args:
            ip: IP address.

        Returns:
            Dictionary with geo fields.
        """
        if not ip:
            return {}

        cache_key = f"geo:{ip}"
        cached = cache.get(cache_key)

        if cached:
            return cached

        data = cls._fetch_geo(ip)

        cache.set(cache_key, data, cls.CACHE_TIMEOUT)
        return data

    @staticmethod
    def _fetch_geo(ip: str) -> Dict[str, Optional[str]]:
        """
        Fetch geo data from provider.

        Args:
            ip: IP address.

        Returns:
            Parsed geo data.
        """
        url = f"https://ipapi.co/{ip}/json/"

        try:
            resp = requests.get(url, timeout=2)

            if resp.status_code != 200:
                logger.warning(
                    f"Geo lookup failed (status={resp.status_code}) for IP {ip}"
                )
                return {}

            payload = resp.json()

            return {
                "city": payload.get("city"),
                "region": payload.get("region"),
                "country": payload.get("country_name"),
                "asn": payload.get("asn"),
            }

        except requests.RequestException as exc:
            logger.warning(
                f"Geo lookup request failed for IP {ip}: {exc}"
            )
            return {}