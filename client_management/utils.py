import requests

def get_geolocation_from_ip(ip_address):
    """
    Fetch geolocation details based on the IP address using IP-API.
    """
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        data = response.json()

        if data['status'] == 'success':
            return {
                "country": data.get("country"),
                "timezone": data.get("timezone"),
            }
        else:
            return {"error": f"IP-API failed: {data.get('message', 'Unknown error')}"}
    except Exception as e:
        return {"error": str(e)}