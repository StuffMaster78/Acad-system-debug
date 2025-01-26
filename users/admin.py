from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for the custom User model.
    """
    model = User
    list_display = ('username', 'email', 'role', 'website', 'created_at', 'updated_at', 'is_active', 'is_staff')
    list_filter = ('role', 'website', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'website__name',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'profile_picture', 'bio', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'profile_picture', 'bio', 'phone')}),
    )