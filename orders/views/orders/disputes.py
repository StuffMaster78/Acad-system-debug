from rest_framework import viewsets
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from orders.models import Dispute
from orders.serializers import DisputeSerializer, DisputeWriterResponseSerializer
from orders.permissions import IsSuperadminOnly
from orders.services.disputes import DisputeService, DisputeWriterResponseService

class DisputeViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for managing Disputes.
    """
    queryset = Dispute.objects.all().select_related('order', 'raised_by')
    serializer_class = DisputeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter disputes based on user role:
        - Superadmins/Admins see all disputes.
        - Users only see disputes they raised.
        """
        user = self.request.user
        if user.is_staff:
            return Dispute.objects.all()
        return Dispute.objects.filter(raised_by=user)

    def perform_create(self, serializer):
        """
        Automatically set the logged-in user as the dispute raiser.
        """
        serializer.save(raised_by=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsSuperadminOnly])
    def resolve_dispute(self, request, pk=None):
        """
        Superadmins resolve a dispute by adding resolution notes and updating the status.
        """
        dispute = get_object_or_404(Dispute, pk=pk)
        resolution_outcome = request.data.get('resolution_outcome')
        resolution_notes = request.data.get("resolution_notes", "")
        extended_deadline = request.data.get('extended_deadline')

        service = DisputeService(dispute)

        try:
            dispute = service.resolve_dispute(
                resolution_outcome=resolution_outcome,
                resolved_by=request.user,
                resolution_notes=resolution_notes,
                extended_deadline=extended_deadline
            )
            return Response(DisputeSerializer(dispute).data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='writer-response')
    def writer_response(self, request, pk=None):
        """
        Writer submits a response to a dispute.
        """
        dispute = self.get_object()
        response_text = request.data.get('response_text')
        response_file = request.data.get('response_file')

        service = DisputeWriterResponseService(dispute, request.user)

        try:
            response = service.submit_response(
                response_text, response_file
            )
            return Response(
                DisputeWriterResponseSerializer(response).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)