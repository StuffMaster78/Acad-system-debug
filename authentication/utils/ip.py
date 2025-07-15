def get_client_ip(request):
    """
    Returns the real IP address of the client, handling proxy headers.
    """

    # Standard reverse proxy header
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # List of IPs, client first, proxy last
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        # Fallback to REMOTE_ADDR
        ip = request.META.get("REMOTE_ADDR")

    return ip