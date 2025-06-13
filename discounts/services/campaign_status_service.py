"""
This module provides a service for managing campaign status metadata.
It includes methods to retrieve badge colors and emojis for different campaign statuses,
and to return a dictionary of UI metadata for a given status.
"""

class CampaignStatusService:
    """
    Handles presentation and logic-related mappings for campaign statuses.
    Provides methods to get badge colors, emojis, and metadata for campaign statuses.
    """

    STATUS_BADGE_MAP = {
        'draft': 'secondary',
        'active': 'success',
        'paused': 'warning',
        'pending': 'info',
        'cancelled': 'danger',
        'deleted': 'dark',
        'completed': 'primary',
        'archived': 'muted',
    }

    STATUS_EMOJI_MAP = {
        'draft': '📝',
        'active': '🔥',
        'paused': '⏸️',
        'pending': '⏳',
        'cancelled': '❌',
        'deleted': '💀',
        'completed': '✅',
        'archived': '📦',
    }

    @classmethod
    def get_badge_color(cls, status):
        """
        Returns the badge color for the given status.
        """
        return cls.STATUS_BADGE_MAP.get(status, 'light')

    @classmethod
    def get_emoji(cls, status):
        """
        Returns the emoji symbol for the given status.
        """
        return cls.STATUS_EMOJI_MAP.get(status, '❓')

    @classmethod
    def get_meta(cls, status):
        """
        Returns a dictionary of UI metadata for a given campaign status.
        """
        return {
            'color': cls.get_badge_color(status),
            'emoji': cls.get_emoji(status)
        }