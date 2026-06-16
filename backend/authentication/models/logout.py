# Compat shim — LogoutEvent was removed; LoginSession now tracks all session state.
# Tests using LogoutEvent.objects.filter(user=...) will get empty querysets.
from django.db import models


class LogoutEvent(models.Model):
    """Stub model — use LoginSession for session tracking instead."""
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="logout_events")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "authentication"
        managed = False  # No DB table — queries return empty results gracefully
