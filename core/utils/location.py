import requests
from django.conf import settings

def get_client_ip(request):
    """
    Get the client's IP address from the request headers.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def get_geolocation_from_ip(ip_address):
    """
    Get geolocation data for a given IP address using an external API.
    Replace the API key and URL with your preferred geolocation provider.
    """
    try:
        api_key = settings.GEOLOCATION_API_KEY  # Add this to your settings
        url = f"http://api.ipstack.com/{ip_address}?access_key={api_key}"

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        geo_data = response.json()

        if "error" in geo_data:
            return {"error": geo_data["error"]["info"]}

        return {
            "ip": geo_data.get("ip"),
            "country": geo_data.get("country_name"),
            "region": geo_data.get("region_name"),
            "city": geo_data.get("city"),
            "latitude": geo_data.get("latitude"),
            "longitude": geo_data.get("longitude"),
            "timezone": geo_data.get("time_zone", {}).get("id"),
        }
    except Exception as e:
        return {"error": str(e)}