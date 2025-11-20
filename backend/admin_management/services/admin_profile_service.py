from django.utils.timezone import now
from django.db import transaction
from admin_management.models import AdminProfile


class AdminProfileService:

    @staticmethod
    def log_admin_action(admin_profile: AdminProfile, action: str):
        admin_profile.update_last_action(action)

    @staticmethod
    def soft_delete(admin_profile: AdminProfile):
        admin_profile.is_active = False
        admin_profile.save(update_fields=["is_active"])

    @staticmethod
    def reactivate(admin_profile: AdminProfile):
        admin_profile.is_active = True
        admin_profile.save(update_fields=["is_active"])
    @staticmethod
    def update_permissions(admin_profile: AdminProfile, **kwargs):
        """
        Update permissions for the admin profile.
        Only updates fields that are provided in kwargs.
        """
        valid_fields = [
            "can_manage_users",
            "can_manage_content",
            "can_access_reports",
            "can_blacklist_users",
            "can_manage_writers",
            "can_manage_clients",
            "can_manage_editors"
        ]
        
        for field in valid_fields:
            if field in kwargs:
                setattr(admin_profile, field, kwargs[field])
        
        admin_profile.save(update_fields=valid_fields)
        return admin_profile
    @staticmethod
    @transaction.atomic
    def create_admin_profile(user, **kwargs):
        """
        Create a new admin profile for the given user.
        This method is atomic to ensure that either the profile is created successfully
        or no changes are made at all.
        """
        admin_profile = AdminProfile(user=user, **kwargs)
        admin_profile.save()
        
        # Assign default permissions
        AdminProfileService.update_permissions(admin_profile, **{
            "can_manage_users": True,
            "can_manage_content": True,
            "can_access_reports": True,
            "can_blacklist_users": False,  # Default to False unless specified
            "can_manage_writers": False,
            "can_manage_clients": False,
            "can_manage_editors": False
        })
        
        return admin_profile 