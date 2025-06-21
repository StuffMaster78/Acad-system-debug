from django.utils.html import format_html
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from client_management.models import ClientProfile
from writer_management.models import WriterProfile
from django.contrib.auth import get_user_model

User = get_user_model()
# Optional inline admin classes for related profiles
class WriterProfileInline(admin.StackedInline):
    model = WriterProfile
    can_delete = False
    verbose_name_plural = "Writer Profile"
    extra = 0

class ClientProfileInline(admin.StackedInline):
    model = ClientProfile
    can_delete = False
    verbose_name_plural = "Client Profile"
    extra = 0

class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for the custom User model.
    """
    model = User

    inlines = [
        WriterProfileInline,
        ClientProfileInline,
        # Add EditorProfileInline, SupportProfileInline, etc. if needed
    ]

    list_display = (
        'id',
        'username',
        'email',
        'role',
        'is_active',
        'is_suspended',
        'is_frozen',
        'is_deletion_requested',
        'deletion_status',
        'deletion_requested_at',
        'deletion_date',
        'is_on_probation',
        'suspension_reason',
        'probation_reason',
        'date_joined',
        'last_login',
        'is_staff',
        'is_superuser',
        'display_avatar',
    )

    list_filter = (
        'role',
        'is_active',
        'is_suspended',
        'is_frozen',
        'is_deletion_requested',
        'is_staff',
        'is_superuser',
    )

    search_fields = ('username', 'email', 'phone_number')
    ordering = ('-date_joined',)

    readonly_fields = (
        'date_joined',
        'last_login',
        'deletion_requested_at',
        'deletion_date',
    )

    fieldsets = (
        (None, {
            'fields': (
                'email',
                'username',
                'password',
                'role',
                'profile_picture',
                'avatar',
                'bio',
                'phone_number',
                'is_available',
            )
        }),
        ('Account Status', {
            'fields': (
                'is_active',
                'is_frozen',
                'is_deletion_requested',
                'is_suspended',
                'is_on_probation',
                'suspension_reason',
                'probation_reason',
                'suspension_start_date',
                'suspension_end_date',
            )
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Impersonation', {
            'fields': ('is_impersonated', 'impersonated_by')
        }),
        ('Deletion Info', {
            'fields': (
                'deletion_requested_at', 'deletion_date', 'deletion_status',
            )
        }),

    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role')
        }),
    )

    # 🧠 Deletion info methods
    def grace_period_days(self, obj):
        if obj.is_deletion_requested and obj.deletion_requested_at:
            return (timezone.now() - obj.deletion_requested_at).days
        return None
    grace_period_days.admin_order_field = 'deletion_requested_at'
    grace_period_days.short_description = "Grace Period (Days)"

    def deletion_status(self, obj):
        if obj.is_frozen:
            return "Frozen"
        if obj.is_deletion_requested:
            return "Pending Deletion"
        return "Active"
    deletion_status.short_description = "Deletion Status"

    ### ADD PERMISSIONS FOR SUPERADMIN
    def has_change_permission(self, request, obj=None):
        """
        Allow Superadmin to edit all users, but restrict lower roles.
        """
        if request.user.role == 'superadmin':
            return True  # Superadmin can edit all users
        if obj and obj.role == 'superadmin':
            return False  # Other roles cannot edit Superadmin
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """
        Allow Superadmin to delete users except themselves.
        """
        if request.user.role == 'superadmin':
            if obj and obj == request.user:
                return False  # Superadmin cannot delete themselves
            return True  # Can delete other users
        return super().has_delete_permission(request, obj)

    def has_add_permission(self, request):
        """
        Allow Superadmin to add new users.
        """
        return request.user.role == 'superadmin' or super().has_add_permission(request)
    
    def has_change_permission(self, request, obj=None):
        if request.user.role == 'superadmin':
            return True
        if obj and obj.role == 'superadmin':
            return False  # Prevent non-superadmins from editing superadmins
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if request.user.role == 'superadmin':
            if obj and obj == request.user:
                return False  # Superadmin cannot delete themselves
            return True  # Superadmin can delete other users
        return super().has_delete_permission(request, obj)

    def profile_picture_preview(self, obj):
        """
        Displays the user's profile picture or selected avatar in the admin panel.
        """
        if obj.profile_picture:
            return format_html('<img src="{}" width="50px" style="border-radius:5px;"/>', obj.profile_picture.url)
        if obj.avatar.startswith('http'):
            return format_html('<img src="{}" width="50px" style="border-radius:5px;"/>', obj.avatar)
        return format_html('<img src="/media/{}" width="50px" style="border-radius:5px;"/>', obj.avatar)

    profile_picture_preview.short_description = "Profile Picture Preview"

    def display_avatar(self, obj):
        """
        Displays the user's avatar or profile picture in list display.
        """
        if obj.profile_picture:
            return format_html('<img src="{}" width="50px" style="border-radius:5px;"/>', obj.profile_picture.url)
        elif obj.avatar:
            if obj.avatar.startswith('http'):
                return format_html('<img src="{}" width="50px" style="border-radius:5px;"/>', obj.avatar)
            return format_html('<img src="/media/{}" width="50px" style="border-radius:5px;"/>', obj.avatar)
        return "No Avatar"

    display_avatar.short_description = "Avatar"


    actions = ['bulk_suspend_users', 'bulk_activate_users']

    def bulk_suspend_users(self, request, queryset):
        """
        Bulk suspend selected users.
        """
        queryset.update(is_suspended=True)
        self.message_user(request, "Selected users have been suspended.")

    bulk_suspend_users.short_description = "Suspend selected users"

    def bulk_activate_users(self, request, queryset):
        """
        Bulk activate selected users.
        """
        queryset.update(is_suspended=False)
        self.message_user(request, "Selected users have been activated.")

    bulk_activate_users.short_description = "Activate selected users"

    def save_model(self, request, obj, form, change):
        """
        Overriding save_model to:
        - Prevent Superadmin from demoting themselves
        - Ensure password hashing is handled correctly
        """
        if change:
            if request.user == obj and obj.role != 'superadmin':
                self.message_user(request, "Superadmin cannot demote themselves!", level="error")
                return

            if 'password' in form.cleaned_data:
                password = form.cleaned_data['password']
                if password and not password.startswith('pbkdf2_sha256$'):  # Avoid double-hashing
                    obj.set_password(password)
        if obj.is_deletion_requested and not obj.deletion_requested_at:
                obj.deletion_requested_at = timezone.now()
        super().save_model(request, obj, form, change)

# Register the custom user admin
admin.site.register(User, CustomUserAdmin)