from django.contrib import admin

from writer_management.models.writer_profile import WriterProfile


@admin.register(WriterProfile)
class WriterProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "account_profile", "pen_name", "verification_status")
    list_filter = ("verification_status", "writer_level", "is_verified")
    search_fields = ("pen_name", "account_profile__user__username", "account_profile__user__email")
