import requests

class GeoService:
    @staticmethod
    def get_geo(ip):
        try:
            resp = requests.get(f"https://ipapi.co/{ip}/json/", timeout=2)
            data = resp.json()
            return {
                "city": data.get("city"),
                "region": data.get("region"),
                "country": data.get("country_name"),
                "asn": data.get("asn"),
            }
        except Exception:
            return {}
