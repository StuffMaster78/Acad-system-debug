from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, WriterLevel


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
        'is_staff',
        'date_joined',
    )
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password', 'role', 'profile_picture', 'avatar', 'bio', 'phone_number')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
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


class WriterLevelAdmin(admin.ModelAdmin):
    """
    Admin configuration for the WriterLevel model.
    """
    model = WriterLevel
    list_display = ('name', 'base_pay_per_page', 'tip_percentage', 'max_orders', 'min_orders', 'min_rating')
    search_fields = ('name',)
    ordering = ('name',)


# Register models with custom admin configurations
admin.site.register(User, CustomUserAdmin)
admin.site.register(WriterLevel, WriterLevelAdmin)