from writer_compensation.exceptions.base import CompensationBaseException


class ExposureLimitBreachedError(CompensationBaseException):
    """
    Risk cap exceeded.
    """


class ExposureMaterializationError(CompensationBaseException):
    """
    Failure in exposure derivation layer.
    """