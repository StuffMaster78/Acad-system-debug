# services/client_feedback_service.py

from orders.models import ClientFeedback
from audit_logging.services import log_audit_action

class ClientFeedbackService:
    """
    Service layer for handling client feedback creation and logic.
    """

    @staticmethod
    def submit_feedback(order, client, rating=None, comment="", is_public=False):
        """
        Creates a new feedback entry.

        Args:
            order (Order): The order the feedback is tied to.
            client (User): The client submitting the feedback.
            rating (int, optional): Rating between 1 and 5.
            comment (str): Optional written feedback.
            is_public (bool): If feedback can be shown to writers or externally.

        Returns:
            ClientFeedback: The saved feedback instance.
        """
        feedback = ClientFeedback.objects.create(
            website=order.website,
            order=order,
            client=client,
            rating=rating,
            comment=comment,
            is_public=is_public
        )

        log_audit_action(
            actor=client,
            action="SUBMIT_CLIENT_FEEDBACK",
            target="feedback.ClientFeedback",
            target_id=feedback.id,
            metadata={
                "order_id": order.id,
                "rating": rating,
                "comment": comment[:50]
            }
        )

        return feedback