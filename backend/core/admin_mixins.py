# core/admin_mixins.py
from django.contrib import admin

class TenantAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(website=request.website)
    def save_model(self, request, obj, form, change):
        if not obj.website_id:
            obj.website = request.website
        super().save_model(request, obj, form, change)