def current_user_metadata(request):
    return {
        "ip_address": getattr(request, "ip", None),
        "user_agent": getattr(request, "user_agent", None),
    }