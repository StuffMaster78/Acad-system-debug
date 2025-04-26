import hashlib
from user_agents import parse as parse_user_agent


def parse_device_info(user_agent_string):
    """
    Parse a User-Agent string to extract device, browser, and OS information.

    Args:
        user_agent_string (str): The raw User-Agent string from the client.

    Returns:
        dict: Dictionary containing browser, OS, device, and platform details.
    """
    if not user_agent_string:
        return {}

    user_agent = parse_user_agent(user_agent_string)

    return {
        "browser": user_agent.browser.family,
        "browser_version": user_agent.browser.version_string,
        "os": user_agent.os.family,
        "os_version": user_agent.os.version_string,
        "device": user_agent.device.family,
        "is_mobile": user_agent.is_mobile,
        "is_tablet": user_agent.is_tablet,
        "is_pc": user_agent.is_pc,
    }

def generate_device_fingerprint(device_info: dict) -> str:
    """
    Generate a simple fingerprint from device info.
    Combines device type, browser, and OS into a hash.
    """
    raw_string = f"{device_info.get('device', '')}|" \
                 f"{device_info.get('browser', '')}|" \
                 f"{device_info.get('os', '')}"
    return hashlib.sha256(raw_string.encode()).hexdigest()


def generate_device_label(device_info: dict) -> str:
    """
    Create a human-readable device label from device info.
    E.g., 'iPhone 15 - Safari'
    """
    device = device_info.get('device', 'Unknown Device')
    browser = device_info.get('browser', 'Unknown Browser')
    return f"{device} - {browser}"

def generate_device_label(device_info: dict) -> str:
    """
    Create a human-readable device label from device info.
    E.g., 'iPhone 15 - Safari'
    """
    device = device_info.get('device', 'Unknown Device')
    browser = device_info.get('browser', 'Unknown Browser')
    return f"{device} - {browser}"