from __future__ import annotations

from notifications_system.registry.template_registry import template_class


@template_class("preferences.reset")
class PreferencesResetTemplate:
    """Template for the preferences reset confirmation email."""

    def __init__(self, context=None):
        self.context = dict(context or {})

    def render(self):
        """Render (title, text, html) for the event."""
        user = self.context.get("user")
        website = self.context.get("website")
        name = getattr(user, "first_name", None) or getattr(user, "username", "")
        site_name = getattr(website, "name", "Our Service")
        domain = getattr(website, "domain", "")

        title = "Your notification preferences were reset"

        text = (
            f"Hi {name},\n\n"
            "Your notification preferences have been reset to defaults.\n"
            "If this wasn't you, please review your preferences or "
            "contact support.\n\n"
            f"Regards,\n{site_name} Team"
        )

        link = f"{domain}/dashboard/settings/notifications" if domain else "#"
        html = (
            f"<p>Hi {name},</p>"
            "<p>Your <strong>notification preferences</strong> have been "
            "reset to the default settings.</p>"
            f"<p>If this wasn't you, please "
            f"<a href='{link}'>review your preferences</a> or contact "
            "support.</p>"
            f"<br><p>Regards,<br>{site_name} Team</p>"
        )

        return title, text, html