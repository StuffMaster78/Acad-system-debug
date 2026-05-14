from reviews_system.models.states import (
    ReviewState,
    ReviewVisibility,
)


class ReviewRules:
    """
    Pure domain rules for review lifecycle.

    This file MUST NOT contain:
        - reputation logic
        - bonus logic
        - external system rules
    """

    @staticmethod
    def is_public(state: str, visibility: str) -> bool:
        """
        A review is public ONLY when:
            - it is approved
            - and explicitly marked public
        """

        return (
            state == ReviewState.APPROVED
            and visibility == ReviewVisibility.PUBLIC
        )

    @staticmethod
    def is_shadowed(visibility: str) -> bool:
        """
        Shadowed reviews are hidden from public UI.
        """

        return visibility == ReviewVisibility.SHADOWED

    @staticmethod
    def is_visible_to_staff(visibility: str) -> bool:
        """
        Staff-visible reviews include internal + shadowed.
        """

        return visibility in (
            ReviewVisibility.INTERNAL,
            ReviewVisibility.SHADOWED,
            ReviewVisibility.UNDER_REVIEW,
        )

    @staticmethod
    def is_removed(state: str, visibility: str) -> bool:
        """
        Fully removed reviews are not usable anywhere.
        """

        return (
            state == ReviewState.REJECTED
            or visibility == ReviewVisibility.REMOVED
        )