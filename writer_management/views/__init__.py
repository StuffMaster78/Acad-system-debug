from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError

from writer_management.models.profile import WriterProfile
from writer_management.models.configs import WriterConfig
from writer_management.models.requests import (
    WriterOrderRequest, WriterOrderTake, WriterDeadlineExtensionRequest,
)
from writer_management.models.discipline import WriterSuspension
from writer_management.models.tickets import WriterSupportTicket
from writer_management.serializers import (
    WriterProfileSerializer, WriterConfigSerializer,
    WriterOrderRequestSerializer, WriterOrderTakeSerializer,
    WriterSuspensionSerializer, WriterSupportTicketSerializer,
    WriterDeadlineExtensionRequestSerializer,
)


class WriterProfileViewSet(viewsets.ModelViewSet):
    queryset = WriterProfile.objects.all()
    serializer_class = WriterProfileSerializer
    permission_classes = [permissions.IsAdminUser]


class WriterConfigViewSet(viewsets.ModelViewSet):
    queryset = WriterConfig.objects.all()
    serializer_class = WriterConfigSerializer
    permission_classes = [permissions.IsAdminUser]


class WriterOrderRequestViewSet(viewsets.ModelViewSet):
    queryset = WriterOrderRequest.objects.all()
    serializer_class = WriterOrderRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        writer = self.request.user.writer_profile
        config = WriterConfig.objects.first()
        if config:
            max_requests = config.max_requests_per_writer
            active_requests = WriterOrderRequest.objects.filter(writer=writer, approved=False).count()
            if active_requests >= max_requests:
                raise ValidationError("Max request limit reached.")
        serializer.save(writer=writer)

    @action(detail=True, methods=['POST'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        request_obj = self.get_object()
        request_obj.approved = True
        request_obj.save()
        return Response({"message": "Order request approved."}, status=status.HTTP_200_OK)


class WriterOrderTakeViewSet(viewsets.ModelViewSet):
    queryset = WriterOrderTake.objects.all()
    serializer_class = WriterOrderTakeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        writer = self.request.user.writer_profile
        config = WriterConfig.objects.first()
        if config and not config.takes_enabled:
            raise ValidationError("Taking orders is disabled.")
        max_allowed_orders = writer.writer_level.max_orders if writer.writer_level else 0
        current_taken_orders = WriterOrderTake.objects.filter(writer=writer).count()
        if current_taken_orders >= max_allowed_orders:
            raise ValidationError("You have reached your max take limit.")
        serializer.save(writer=writer)


class WriterSupportTicketViewSet(viewsets.ModelViewSet):
    queryset = WriterSupportTicket.objects.all()
    serializer_class = WriterSupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated]


class WriterSuspensionViewSet(viewsets.ModelViewSet):
    queryset = WriterSuspension.objects.all()
    serializer_class = WriterSuspensionSerializer
    permission_classes = [permissions.IsAdminUser]


class WriterDeadlineExtensionRequestViewSet(viewsets.ModelViewSet):
    queryset = WriterDeadlineExtensionRequest.objects.all()
    serializer_class = WriterDeadlineExtensionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

