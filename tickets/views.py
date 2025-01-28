from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Ticket, TicketMessage
from .serializers import TicketSerializer, TicketMessageSerializer


class TicketViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tickets.
    """
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve', 'partial_update']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['destroy', 'escalate', 'reopen']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def escalate(self, request, pk=None):
        ticket = self.get_object()
        ticket.is_escalated = True
        ticket.save()
        return Response({'status': 'Ticket escalated'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reopen(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status == 'closed':
            ticket.status = 'open'
            ticket.save()
            return Response({'status': 'Ticket reopened'}, status=status.HTTP_200_OK)
        return Response({'error': 'Ticket is not closed'}, status=status.HTTP_400_BAD_REQUEST)


class TicketMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing ticket messages.
    """
    queryset = TicketMessage.objects.all()
    serializer_class = TicketMessageSerializer

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)