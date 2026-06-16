# Compatibility shim — serializers are now in authentication.api.serializers.*
# Tests referencing RegisterSerializer need to be updated.
from authentication.api.serializers.registration_serializers import (
    RegistrationRequestSerializer as RegisterSerializer,
)

__all__ = ["RegisterSerializer"]
