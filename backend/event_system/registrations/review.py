from event_system.registry import EventRegistry
from event_system.consumers.review_event_consumer import ReviewEventConsumer


def register_review_events() -> None:
    EventRegistry.register("review.approved", ReviewEventConsumer.handle_approved)
    EventRegistry.register("review.shadowed", ReviewEventConsumer.handle_shadowed)
    EventRegistry.register("review.rejected", ReviewEventConsumer.handle_rejected)