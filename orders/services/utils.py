from datetime import timedelta, datetime, timezone
from order_configs.models import RevisionPolicyConfig

def get_order_config(website):
    """
    Retrieves the active revision policy config for a specific website.
    
    Args:
        website (Website): The website associated with the order.

    Returns:
        RevisionPolicyConfig: The active revision policy, or None if not found.
    """
    return RevisionPolicyConfig.objects.filter(website=website, active=True).first()


def check_if_urgent(data: dict) -> bool:
    deadline = data.get("deadline")
    if not deadline:
        return False

    now = datetime.now(timezone.utc)
    urgent_threshold = timedelta(hours=6)  # Or 6, 24 — you decide
    return deadline - now < urgent_threshold


def is_admin_or_support(self) -> bool:
        """
        Check if the user is an admin or support.
        """
        return self.user.is_staff or self.user.role in ['support', 'admin']