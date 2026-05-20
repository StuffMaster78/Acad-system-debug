from superadmin_management.services.appeal_service import AppealService
from superadmin_management.services.blacklist_service import BlacklistService
from superadmin_management.services.user_governance_service import (
    UserGovernanceService,
)


class SuperadminService:

    @staticmethod
    def create_user(**kwargs):
        return UserGovernanceService.create_user(**kwargs)

    @staticmethod
    def change_user_role(**kwargs):
        return UserGovernanceService.change_role(**kwargs)

    @staticmethod
    def blacklist(**kwargs):
        return BlacklistService.blacklist(**kwargs)

    @staticmethod
    def lift_blacklist(**kwargs):
        return BlacklistService.lift_blacklist(**kwargs)

    @staticmethod
    def approve_appeal(**kwargs):
        return AppealService.approve(**kwargs)

    @staticmethod
    def reject_appeal(**kwargs):
        return AppealService.reject(**kwargs)
