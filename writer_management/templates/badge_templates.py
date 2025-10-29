# writer_management/templates/badge_templates.py

from notifications_system.templates.base import BaseNotificationTemplate
from notifications_system.registry.template_registry import register_template_class
from typing import Dict, Tuple


@register_template_class("badge.awarded")
class BadgeAwardedTemplate(BaseNotificationTemplate):
    """Template for badge awarded notifications."""
    event_name = "badge.awarded"

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        badge_name = ctx.get("badge_name", "New Badge")
        badge_icon = ctx.get("badge_icon", "🏆")
        badge_description = ctx.get("badge_description", "Congratulations on your achievement!")
        writer_name = ctx.get("writer_name", "Writer")
        is_auto = ctx.get("is_auto_awarded", False)
        frontend_url = ctx.get("frontend_url", "#")

        title = f"{badge_icon} Congratulations! You earned the {badge_name} badge!"
        text = f"Hello {writer_name},\n\nYou have been awarded the {badge_name} badge! {badge_description}\n\nKeep up the excellent work!"
        html = f"""
        <html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">{badge_icon} {badge_name} Badge Earned!</h1>
            </div>
            <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; color: #333;">Hello {writer_name},</p>
                <p style="font-size: 16px; color: #333;">Congratulations! You have been awarded the <strong>{badge_name}</strong> badge!</p>
                <p style="font-size: 14px; color: #666; background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0;">{badge_description}</p>
                <p style="font-size: 16px; color: #333;">Keep up the excellent work!</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{frontend_url}/badges" style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">View Your Badges</a>
                </div>
                <p style="font-size: 12px; color: #999; text-align: center;">{'Automatically awarded based on your performance' if is_auto else 'Awarded by administrator'}</p>
            </div>
        </body></html>
        """
        return title, text, html


@register_template_class("badge.revoked")
class BadgeRevokedTemplate(BaseNotificationTemplate):
    """Template for badge revoked notifications."""
    event_name = "badge.revoked"

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        badge_name = ctx.get("badge_name", "Badge")
        badge_icon = ctx.get("badge_icon", "🏆")
        writer_name = ctx.get("writer_name", "Writer")
        revoked_reason = ctx.get("revoked_reason", "No reason provided")
        revoked_by = ctx.get("revoked_by", "Administrator")
        frontend_url = ctx.get("frontend_url", "#")

        title = f"Badge Update: {badge_name} badge has been revoked"
        text = f"Hello {writer_name},\n\nYour {badge_name} badge has been revoked.\n\nReason: {revoked_reason}\n\nRevoked by: {revoked_by}"
        html = f"""
        <html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #dc3545; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">{badge_icon} Badge Revoked</h1>
            </div>
            <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; color: #333;">Hello {writer_name},</p>
                <p style="font-size: 16px; color: #333;">Your <strong>{badge_name}</strong> badge has been revoked.</p>
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0; font-size: 14px; color: #856404;"><strong>Reason:</strong> {revoked_reason}</p>
                    <p style="margin: 5px 0 0 0; font-size: 14px; color: #856404;"><strong>Revoked by:</strong> {revoked_by}</p>
                </div>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{frontend_url}/badges" style="background: #6c757d; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">View Your Badges</a>
                </div>
            </div>
        </body></html>
        """
        return title, text, html


@register_template_class("badge.milestone")
class BadgeMilestoneTemplate(BaseNotificationTemplate):
    """Template for badge milestone notifications."""
    event_name = "badge.milestone"

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        milestone = ctx.get("milestone", "Milestone")
        count = ctx.get("count", 0)
        writer_name = ctx.get("writer_name", "Writer")
        frontend_url = ctx.get("frontend_url", "#")

        title = f"🎯 Milestone Achieved: {milestone}"
        text = f"Hello {writer_name},\n\nCongratulations! You've reached a new milestone: {milestone}\n\nCount: {count}\n\nKeep up the great work!"
        html = f"""
        <html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">🎯 Milestone Achieved!</h1>
            </div>
            <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; color: #333;">Hello {writer_name},</p>
                <p style="font-size: 16px; color: #333;">Congratulations! You've reached a new milestone:</p>
                <div style="background: #e3f2fd; border: 2px solid #2196f3; padding: 20px; border-radius: 10px; margin: 20px 0; text-align: center;">
                    <h2 style="margin: 0 0 10px 0; color: #1976d2; font-size: 20px;">{milestone}</h2>
                    <p style="margin: 0; font-size: 18px; color: #1976d2; font-weight: bold;">Count: {count}</p>
                </div>
                <p style="font-size: 16px; color: #333;">Keep up the great work!</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{frontend_url}/badges" style="background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">View Your Progress</a>
                </div>
            </div>
        </body></html>
        """
        return title, text, html


@register_template_class("badge.leaderboard")
class BadgeLeaderboardTemplate(BaseNotificationTemplate):
    """Template for badge leaderboard notifications."""
    event_name = "badge.leaderboard"

    def render(self, context: Dict | None = None) -> Tuple[str, str, str]:
        ctx = {**self.context, **(context or {})}
        position = ctx.get("position", 0)
        total_writers = ctx.get("total_writers", 0)
        badge_name = ctx.get("badge_name", "Badge")
        writer_name = ctx.get("writer_name", "Writer")
        frontend_url = ctx.get("frontend_url", "#")

        title = f"🏆 Leaderboard Update: You're #{position} for {badge_name} badge!"
        text = f"Hello {writer_name},\n\nGreat news! You're now #{position} out of {total_writers} writers for the {badge_name} badge!\n\nKeep up the excellent work!"
        html = f"""
        <html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); color: #8b4513; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">🏆 Leaderboard Update!</h1>
            </div>
            <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; color: #333;">Hello {writer_name},</p>
                <p style="font-size: 16px; color: #333;">Great news! You're now <strong>#{position}</strong> out of {total_writers} writers for the <strong>{badge_name}</strong> badge!</p>
                <div style="background: #fff3cd; border: 2px solid #ffc107; padding: 20px; border-radius: 10px; margin: 20px 0; text-align: center;">
                    <h2 style="margin: 0 0 10px 0; color: #856404; font-size: 18px;">Your Ranking</h2>
                    <p style="margin: 0; font-size: 24px; color: #856404; font-weight: bold;">#{position} of {total_writers}</p>
                </div>
                <p style="font-size: 16px; color: #333;">Keep up the excellent work!</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{frontend_url}/leaderboard" style="background: #17a2b8; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">View Leaderboard</a>
                </div>
            </div>
        </body></html>
        """
        return title, text, html
