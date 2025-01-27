from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for the custom User model.
    """
    model = User
    list_display = (
        'id',
        'username',
        'email',
        'role',
        'is_active',
        'is_frozen',
        'is_deletion_requested',
        'date_joined',
        'last_login',
    )
    list_filter = ('role', 'is_active', 'is_frozen', 'is_deletion_requested', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login', 'deletion_requested_at', 'deletion_date')

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
                'phone_number'
            )
        }),
        ('Account Status', {
            'fields': (
                'is_active', 
                'is_frozen', 
                'is_deletion_requested', 
                'deletion_requested_at', 
                'deletion_date'
            )
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Writer Details', {
            'fields': ('writer_level', 'verification_documents', 'rating', 'completed_orders')
        }),
        ('Editor Details', {
            'fields': ('edited_orders',)
        }),
        ('Support Details', {
            'fields': ('handled_tickets', 'resolved_orders')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role')
        }),
    )



# Register models with custom admin configurations
admin.site.register(User, CustomUserAdmin)
