from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView


class ServicePageSchemaView(APIView):
    """GET /cms-api/service-pages/schema/<page_id>/"""

    permission_classes = [permissions.AllowAny]

    def get(self, request, page_id):
        from wagtail.models import Page

        try:
            page = Page.objects.live().get(pk=page_id).specific
        except Page.DoesNotExist:
            return Response({"error": "Page not found"}, status=404)

        from cms_service_pages.serializers import ServicePageSchemaOrgSerializer

        schema = ServicePageSchemaOrgSerializer().to_representation(page)
        return Response(schema)
