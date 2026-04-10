class PaymentProviderError(Exception):
    """Base provider error."""


class PaymentProviderConfigurationError(PaymentProviderError):
    """Raised when provider configuration is missing or invalid."""


class PaymentProviderWebhookError(PaymentProviderError):
    """Raised when webhook validation or parsing fails."""


class PaymentProviderRefundError(PaymentProviderError):
    """Raised when refund initiation fails."""


class PaymentProviderVerificationError(PaymentProviderError):
    """Raised when payment verification fails."""