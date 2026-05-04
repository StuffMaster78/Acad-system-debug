from __future__ import annotations

from rest_framework.throttling import UserRateThrottle


class ClassAccessViewThrottle(UserRateThrottle):
    scope = "class_access_view"


class ClassTwoFactorThrottle(UserRateThrottle):
    scope = "class_two_factor"


class ClassPaymentPrepareThrottle(UserRateThrottle):
    scope = "class_payment_prepare"


class ClassProposalActionThrottle(UserRateThrottle):
    scope = "class_proposal_action"