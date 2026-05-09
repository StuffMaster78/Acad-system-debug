from writer_payments_management.exceptions.base import PaymentsBaseException


class ExposureLimitBreachedError(PaymentsBaseException):
    """
    Risk cap exceeded.
    """


class ExposureMaterializationError(PaymentsBaseException):
    """
    Failure in exposure derivation layer.
    """