from django.utils import timezone
from reviews_system.models.order_review import WebsiteReview
from reviews_system.models.writer_review import WriterReview
from reviews_system.models.order_review import OrderReview
from notifications_system.services.core import NotificationService

class ReviewModerationService:
    """
    Service to moderate and manage reviews across Website, Writer, and Order.
    Supports shadowing, flagging, approving, and deleting reviews.
    """

    @staticmethod
    def _get_review_type(review) -> str:
        """
        Determines the type of review based on its class.
        """
        if isinstance(review, OrderReview):
            return "order"
        elif isinstance(review, WriterReview):
            return "writer"
        elif isinstance(review, WebsiteReview):
            return "website"
        return "unknown"

    @staticmethod
    def moderate_review(review, data: dict):
        """
        Applies moderation decisions to a review object.

        Args:
            review (Model): The review instance
                (OrderReview, WriterReview, WebsiteReview).
            data (dict): Dictionary with keys 
                    like `is_approved`, `is_shadowed`, `flag_reason`, etc.
        """
        if "is_approved" in data:
            """
            Approving a review means marking it as valid and visible to the public.
            """
            review.is_approved = data["is_approved"]

        if "is_shadowed" in data:
            """
            Shadowing a review means marking it as not visible to the public,
            but still keeping it in the database for internal review.
            """
            review.is_shadowed = data["is_shadowed"]

        if "is_flagged" in data:
            """
            Flagging a review means marking it for further investigation,
            usually due to inappropriate content or disputes.
            """
            review.is_flagged = data["is_flagged"]

        if "flag_reason" in data:
            """
            The reason for flagging a review, which
            can be used for internal tracking.
            """
            review.flag_reason = data["flag_reason"]

        if "moderation_notes" in data:
            """
            Additional notes from the moderator about the review.
            This can include explanations for the moderation decision.
            """
            review.moderation_notes = data["moderation_notes"]

        review.moderated_at = timezone.now()
        review.save(
            update_fields=[
                "is_approved", "is_shadowed", "is_flagged",
                "flag_reason", "moderation_notes", "moderated_at"
            ]
        )

    @staticmethod
    def delete_review(review):
        """
        Permanently deletes a review instance.

        Args:
            review (Model): The review to delete.
        """
        review.delete()

    @staticmethod
    def approve_review(review):
        """
        Approves a review, making it visible to the public.
        """
        if not review.is_approved:
            review.is_approved = True
            review.moderated_at = timezone.now()
            review.save(update_fields=["is_approved", "moderated_at"])

        NotificationService.send_notification(
            recipient=review.user,
            title="Review Approved",
            message=f"Your {ReviewModerationService._get_review_type(review)} review has been approved and is now visible.",
            category="reviews"
        )

    @staticmethod
    def shadow_review(review, reason: str = ""):
        """
        Shadows a review, making it not visible to the public.
        """
        if review.is_approved:
            review.is_approved = False
        if not review.is_shadowed:
            review.is_shadowed = True
            review.flag_reason = reason
            review.moderated_at = timezone.now()
            review.save(
                update_fields=[
                    "is_shadowed",
                    "flag_reason",
                    "moderated_at"
                ]
            )

    @staticmethod
    def unshadow_review(review):
        """
        Unshadows a review, making it visible to the public again.
        """
        review.is_shadowed = False
        review.flag_reason = None
        review.moderated_at = timezone.now()
        review.save(
            update_fields=[
                "is_shadowed", "flag_reason", "moderated_at"
            ]
        )

    @staticmethod
    def flag_review(review, reason: str):
        """
        Flags a review for further investigation.
        """
        review.is_flagged = True
        review.flag_reason = reason
        review.moderated_at = timezone.now()
        review.save(
            update_fields=[
                "is_flagged",
                "flag_reason",
                "moderated_at"
            ]
        )