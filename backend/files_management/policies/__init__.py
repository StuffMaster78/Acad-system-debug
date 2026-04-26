"""
Policy exports and registration for files_management.
"""

from files_management.policies.base import BaseFilePolicy
from files_management.policies.class_file_policy import ClassFilePolicy
from files_management.policies.cms_file_policy import CmsFilePolicy
from files_management.policies.default_file_policy import DefaultFilePolicy
from files_management.policies.message_file_policy import MessageFilePolicy
from files_management.policies.order_file_policy import OrderFilePolicy
from files_management.policies.profile_file_policy import ProfileFilePolicy
from files_management.policies.registry import FilePolicyRegistry
from files_management.policies.support_file_policy import SupportFilePolicy


def register_default_file_policies() -> None:
    """
    Register built-in file policies.

    Domain-specific policies should be registered before the default
    fallback policy.
    """

    FilePolicyRegistry.register(policy=OrderFilePolicy())
    FilePolicyRegistry.register(policy=MessageFilePolicy())
    FilePolicyRegistry.register(policy=ProfileFilePolicy())
    FilePolicyRegistry.register(policy=CmsFilePolicy())
    FilePolicyRegistry.register(policy=SupportFilePolicy())
    FilePolicyRegistry.register(policy=ClassFilePolicy())
    FilePolicyRegistry.register(policy=DefaultFilePolicy())


__all__ = [
    "BaseFilePolicy",
    "ClassFilePolicy",
    "CmsFilePolicy",
    "DefaultFilePolicy",
    "FilePolicyRegistry",
    "MessageFilePolicy",
    "OrderFilePolicy",
    "ProfileFilePolicy",
    "SupportFilePolicy",
    "register_default_file_policies",
]