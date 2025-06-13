"""
A service to manage discount status mappings."""

class DiscountStatusService:
    """
    Maps discount status values to badge styles, emojis, and optional metadata.
    """

    STATUS_BADGE_MAP = {
        'draft': 'secondary',
        'active': 'success',
        'expired': 'danger',
        'paused': 'warning',
        'scheduled': 'info',
        'disabled': 'dark',
        'archived': 'muted',
        'deleted': 'light',
    }

    STATUS_EMOJI_MAP = {
        'draft': '📝',
        'active': '🔥',
        'expired': '💀',
        'paused': '⏸️',
        'scheduled': '📅',
        'disabled': '🚫',
        'archived': '📦',
        'deleted': '🗑️',
    }

    STATUS_LABEL_MAP = {
        'draft': 'Draft',
        'active': 'Active',
        'expired': 'Expired',
        'paused': 'Paused',
        'scheduled': 'Scheduled',
        'disabled': 'Disabled',
        'archived': 'Archived',
    }

    @classmethod
    def get_badge_color(cls, status):
        return cls.STATUS_BADGE_MAP.get(status, 'light')

    @classmethod
    def get_emoji(cls, status):
        return cls.STATUS_EMOJI_MAP.get(status, '❓')

    @classmethod
    def get_label(cls, status):
        return cls.STATUS_LABEL_MAP.get(status, status.capitalize())

    @classmethod
    def get_meta(cls, status):
        return {
            'label': cls.get_label(status),
            'emoji': cls.get_emoji(status),
            'color': cls.get_badge_color(status)
        }