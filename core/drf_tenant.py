# core/drf_tenant.py
from rest_framework.viewsets import ModelViewSet

class TenantViewSet(ModelViewSet):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs  # already scoped by default manager
    def perform_create(self, serializer):
        serializer.save(website=self.request.website)