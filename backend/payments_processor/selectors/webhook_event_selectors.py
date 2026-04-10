from typing import Optional

from payments_processor.models.payment_intent import PaymentIntent


def get_payment_intent_by_reference(reference: str) -> Optional[PaymentIntent]:
    """
    Return a payment intent by its internal reference.
    """
    return (
        PaymentIntent.objects.select_related("customer")
        .filter(reference=reference)
        .first()
    )


def get_payment_intent_by_provider_intent_id(
    provider: str,
    provider_intent_id: str,
) -> Optional[PaymentIntent]:
    """
    Return a payment intent by provider and provider intent identifier.
    """
    return (
        PaymentIntent.objects.select_related("customer")
        .filter(
            provider=provider,
            provider_intent_id=provider_intent_id,
        )
        .first()
    )