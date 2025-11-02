"""
Loyalty and redemption notification templates.
"""
from notifications_system.templates.base import BaseNotificationTemplate
from notifications_system.registry.template_registry import register_template


@register_template("loyalty.points_awarded")
class PointsAwardedTemplate(BaseNotificationTemplate):
    """Notification when loyalty points are awarded."""
    
    def get_title(self, payload: dict) -> str:
        points = payload.get("points", 0)
        return f"🎉 {points} Loyalty Points Awarded!"
    
    def get_message(self, payload: dict) -> str:
        points = payload.get("points", 0)
        reason = payload.get("reason", "for your purchase")
        total_points = payload.get("total_points", points)
        message = f"You've earned {points} loyalty points {reason}. "
        message += f"Your total points balance is now {total_points}."
        return message
    
    def get_link(self, payload: dict) -> str:
        return "/account/loyalty"


@register_template("loyalty.tier_upgraded")
class TierUpgradedTemplate(BaseNotificationTemplate):
    """Notification when loyalty tier is upgraded."""
    
    def get_title(self, payload: dict) -> str:
        tier_name = payload.get("tier_name", "new tier")
        return f"🌟 Upgraded to {tier_name}!"
    
    def get_message(self, payload: dict) -> str:
        tier_name = payload.get("tier_name", "new tier")
        perks = payload.get("perks", "")
        message = (
            f"Congratulations! You've been upgraded to {tier_name} tier. "
        )
        if perks:
            message += f"New benefits: {perks}. "
        message += "Thank you for your continued loyalty!"
        return message
    
    def get_link(self, payload: dict) -> str:
        return "/account/loyalty"


@register_template("loyalty.redemption.approved")
class RedemptionApprovedTemplate(BaseNotificationTemplate):
    """Notification when redemption request is approved."""
    
    def get_title(self, payload: dict) -> str:
        item_name = payload.get("item_name", "Redemption item")
        return f"Redemption Approved: {item_name}"
    
    def get_message(self, payload: dict) -> str:
        item_name = payload.get("item_name", "redemption item")
        points_used = payload.get("points_used", 0)
        fulfillment_code = payload.get("fulfillment_code", "")
        message = (
            f"Your redemption request for '{item_name}' using {points_used} points "
            f"has been approved! "
        )
        if fulfillment_code:
            message += f"Your code: {fulfillment_code}. "
        message += "Enjoy your reward!"
        return message
    
    def get_link(self, payload: dict) -> str:
        redemption_id = payload.get("redemption_id")
        return f"/account/loyalty/redemptions/{redemption_id}" if redemption_id else "/account/loyalty"


@register_template("loyalty.redemption.rejected")
class RedemptionRejectedTemplate(BaseNotificationTemplate):
    """Notification when redemption request is rejected."""
    
    def get_title(self, payload: dict) -> str:
        return "Redemption Request Rejected"
    
    def get_message(self, payload: dict) -> str:
        item_name = payload.get("item_name", "redemption item")
        points_used = payload.get("points_used", 0)
        rejection_reason = payload.get("rejection_reason", "Unable to process")
        message = (
            f"Your redemption request for '{item_name}' using {points_used} points "
            f"was rejected. Reason: {rejection_reason}. "
        )
        message += f"Your {points_used} points have been refunded to your account."
        return message
    
    def get_link(self, payload: dict) -> str:
        return "/account/loyalty/redemptions"


@register_template("loyalty.milestone_reached")
class MilestoneReachedTemplate(BaseNotificationTemplate):
    """Notification when loyalty milestone is reached."""
    
    def get_title(self, payload: dict) -> str:
        milestone_name = payload.get("milestone_name", "Milestone")
        return f"🏆 Milestone Achieved: {milestone_name}!"
    
    def get_message(self, payload: dict) -> str:
        milestone_name = payload.get("milestone_name", "milestone")
        reward_points = payload.get("reward_points", 0)
        message = f"Congratulations! You've reached the '{milestone_name}' milestone. "
        if reward_points > 0:
            message += f"You've earned {reward_points} bonus points! "
        message += "Keep up the great work!"
        return message
    
    def get_link(self, payload: dict) -> str:
        return "/account/loyalty/milestones"


@register_template("loyalty.badge_awarded")
class BadgeAwardedTemplate(BaseNotificationTemplate):
    """Notification when badge is awarded."""
    
    def get_title(self, payload: dict) -> str:
        badge_name = payload.get("badge_name", "Badge")
        return f"🏅 Badge Earned: {badge_name}!"
    
    def get_message(self, payload: dict) -> str:
        badge_name = payload.get("badge_name", "badge")
        description = payload.get("description", "")
        message = f"You've earned the '{badge_name}' badge! "
        if description:
            message += f"{description} "
        message += "Show it off on your profile!"
        return message
    
    def get_link(self, payload: dict) -> str:
        return "/account/badges"

