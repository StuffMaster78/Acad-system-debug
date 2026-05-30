"""
Exposes governance models under the 'governance' app label.
The concrete models live in governance/policies/models.py.
"""
from governance.policies.models import Policy, PolicyDecisionLog, PolicyVersion

__all__ = ["Policy", "PolicyVersion", "PolicyDecisionLog"]
