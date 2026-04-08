from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from authentication.services.login_session_service import (
    LoginSessionService,
)
from authentication.services.refresh_token_policy_service import (
    RefreshTokenPolicyService,
)


class SessionAwareTokenRefreshSerializer(TokenRefreshSerializer):
    """
    Refresh serializer that validates the backing LoginSession before
    issuing new tokens.
    """

    def validate(self, attrs):
        raw_refresh_token = attrs["refresh"]
        request = self.context.get("request")

        refresh, user, session = RefreshTokenPolicyService.validate_refresh(
            raw_refresh_token=raw_refresh_token,
            request=request,
        )

        data = super().validate(attrs)

        # Sliding activity: refresh use counts as activity.
        LoginSessionService.touch_session(session=session)

        return data