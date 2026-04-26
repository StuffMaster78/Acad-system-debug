from __future__ import annotations

from files_management.models import FileAttachment
from files_management.policies.base import BaseFilePolicy


class FilePolicyRegistry:
    """
    Registry for domain specific file policies.

    The registry allows files_management to stay generic while domain
    apps still define their own access rules. Policies are evaluated in
    registration order, with default policy as the final fallback.
    """

    _policies: list[BaseFilePolicy] = []

    @classmethod
    def register(cls, *, policy: BaseFilePolicy) -> None:
        """
        Register a policy instance if it has not already been added.
        """

        policy_class = policy.__class__

        if any(isinstance(item, policy_class) for item in cls._policies):
            return

        cls._policies.append(policy)

    @classmethod
    def get_policy(
        cls,
        *,
        attachment: FileAttachment,
    ) -> BaseFilePolicy | None:
        """
        Return the first policy that supports an attachment.
        """

        for policy in cls._policies:
            if policy.supports(attachment=attachment):
                return policy

        return None

    @classmethod
    def clear(cls) -> None:
        """
        Clear registered policies.

        This is mostly useful in tests.
        """

        cls._policies.clear()