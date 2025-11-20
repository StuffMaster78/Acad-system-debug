from typing import Any, Mapping, Optional, TYPE_CHECKING
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from django.core.exceptions import ObjectDoesNotExist

from notifications_system.services.core import NotificationService
from notifications_system.registry.role_registry import register_role
from notifications_system.models.notifications import NotificationType
from writer_management.models.badges import WriterBadge  # Badge not used, drop it
from writer_management.models.profile import WriterProfile

logger = logging.getLogger(__name__)

User = get_user_model()


if TYPE_CHECKING:
    # Import your concrete user model for type-checkers only
    # adjust path if different
    from users.models import User as ConcreteUser

def writer_role_resolver(context: Mapping[str, Any]) -> Optional["ConcreteUser"]:
    """
    Resolver for the 'writer' role.

    Returns the User if context contains a writer user; otherwise None.
    """
    # Start with 'user' if present
    user: Optional[AbstractBaseUser] = context.get("user")  # type: ignore[assignment]

    # Fallbacks: writer / writer_profile -> .user
    if user is None:
        writer_profile: Optional[WriterProfile] = (
            context.get("writer") or context.get("writer_profile")
        )
        if writer_profile is not None:
            u = getattr(writer_profile, "user", None)
            if u is not None:
                user = u

    if user is None or isinstance(user, AnonymousUser):
        return None

    # Access reverse OneToOne safely
    try:
        _ = user.writer_profile  # may raise ObjectDoesNotExist
    except ObjectDoesNotExist:
        return None
    except Exception:
        # Be defensive; don't crash the resolver
        return None

    return user  # type: ignore[return-value]


def send_badge_awarded_notification(writer_badge: WriterBadge) -> bool:
    """
    Send notification when a writer receives a new badge.
    
    Args:
        writer_badge: The WriterBadge instance that was just awarded
        
    Returns:
        bool: True if notification was sent successfully
    """
    try:
        writer = writer_badge.writer
        badge = writer_badge.badge
        
        # Prepare notification payload
        payload = {
            "badge_name": badge.name,
            "badge_icon": badge.icon,
            "badge_type": badge.type,
            "badge_description": badge.description,
            "writer_name": writer.user.get_full_name() or writer.user.username,
            "awarded_at": writer_badge.issued_at.isoformat(),
            "is_auto_awarded": writer_badge.is_auto_awarded,
            "badge_id": badge.id,
            "writer_badge_id": writer_badge.id,
        }
        
        # Send notification to the writer
        notification = NotificationService.send_notification(
            event="badge.awarded",
            user=writer.user,
            payload=payload,
            channels=[NotificationType.IN_APP, NotificationType.EMAIL],
            website_id=getattr(writer, 'website_id', None)
        )
        
        if notification:
            logger.info(f"Badge awarded notification sent to writer {writer.user.id} for badge {badge.name}")
            return True
        else:
            logger.warning(f"Failed to send badge awarded notification to writer {writer.user.id}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending badge awarded notification: {e}")
        return False


def send_badge_revoked_notification(writer_badge: WriterBadge) -> bool:
    """
    Send notification when a writer's badge is revoked.
    
    Args:
        writer_badge: The WriterBadge instance that was revoked
        
    Returns:
        bool: True if notification was sent successfully
    """
    try:
        writer = writer_badge.writer
        badge = writer_badge.badge
        
        # Prepare notification payload
        payload = {
            "badge_name": badge.name,
            "badge_icon": badge.icon,
            "badge_type": badge.type,
            "writer_name": writer.user.get_full_name() or writer.user.username,
            "revoked_at": writer_badge.revoked_at.isoformat() if writer_badge.revoked_at else None,
            "revoked_reason": writer_badge.revoked_reason,
            "revoked_by": writer_badge.revoked_by.get_full_name() if writer_badge.revoked_by else "System",
            "badge_id": badge.id,
            "writer_badge_id": writer_badge.id,
        }
        
        # Send notification to the writer
        notification = NotificationService.send_notification(
            event="badge.revoked",
            user=writer.user,
            payload=payload,
            channels=[NotificationType.IN_APP, NotificationType.EMAIL],
            website_id=getattr(writer, 'website_id', None)
        )
        
        if notification:
            logger.info(f"Badge revoked notification sent to writer {writer.user.id} for badge {badge.name}")
            return True
        else:
            logger.warning(f"Failed to send badge revoked notification to writer {writer.user.id}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending badge revoked notification: {e}")
        return False


def send_badge_milestone_notification(writer: WriterProfile, milestone: str, count: int) -> bool:
    """
    Send notification when a writer reaches a badge milestone.
    
    Args:
        writer: The WriterProfile instance
        milestone: The milestone description
        count: The count that triggered the milestone
        
    Returns:
        bool: True if notification was sent successfully
    """
    try:
        # Prepare notification payload
        payload = {
            "milestone": milestone,
            "count": count,
            "writer_name": writer.user.get_full_name() or writer.user.username,
            "achieved_at": writer.user.date_joined.isoformat(),
            "writer_id": writer.id,
        }
        
        # Send notification to the writer
        notification = NotificationService.send_notification(
            event="badge.milestone",
            user=writer.user,
            payload=payload,
            channels=[NotificationType.IN_APP, NotificationType.EMAIL],
            website_id=getattr(writer, 'website_id', None)
        )
        
        if notification:
            logger.info(f"Badge milestone notification sent to writer {writer.user.id} for milestone {milestone}")
            return True
        else:
            logger.warning(f"Failed to send badge milestone notification to writer {writer.user.id}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending badge milestone notification: {e}")
        return False


def register_badge_notification_roles():
    """Register notification roles for the badge system."""
    
    # Register writer role for badge notifications
    register_role(
        "writer",
        writer_role_resolver,
        channels={
            "badge.awarded": {"in_app", "email"},
            "badge.revoked": {"in_app", "email"},
            "badge.milestone": {"in_app", "email"},
        }
    )
    
    logger.info("Badge notification roles registered successfully")


# Auto-register roles when module is imported
register_badge_notification_roles()
