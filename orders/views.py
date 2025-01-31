from rest_framework import viewsets, permissions
from .models import Order, PaymentTransaction
from .serializers import OrderSerializer, OrderCreateSerializer, PaymentTransactionSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

class OrderViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for managing Orders.
    """
    queryset = Order.objects.all().select_related('client', 'writer', 'preferred_writer', 'discount_code', 'website')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """
        Return the appropriate serializer based on the action.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        """
        Return the queryset based on the user's role.
        - Admins and support can see all orders.
        - Clients can see only their orders.
        """
        user = self.request.user
        if user.is_staff:  # Admin or support
            return Order.objects.all()
        return Order.objects.filter(client=user)

    def perform_create(self, serializer):
        """
        Automatically assign the authenticated user as the client when creating an order.
        """
        serializer.save(client=self.request.user)

    def perform_update(self, serializer):
        """
        Additional logic during order updates (if required).
        """
        serializer.save()


class PaymentTransactionListView(generics.ListAPIView):
    """Get all payment transactions (Admin Only)"""
    queryset = PaymentTransaction.objects.all()
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAdminUser]

class PaymentTransactionDetailView(generics.RetrieveAPIView):
    """Retrieve a single transaction"""
    queryset = PaymentTransaction.objects.all()
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAdminUser]

class PaymentTransactionCreateView(generics.CreateAPIView):
    """Create a new transaction"""
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        order = request.data.get("order")
        transaction_id = request.data.get("transaction_id")
        amount = request.data.get("amount")
        payment_method = request.data.get("payment_method", "")

        if PaymentTransaction.objects.filter(transaction_id=transaction_id).exists():
            return Response({"detail": "Transaction ID already exists."}, status=status.HTTP_400_BAD_REQUEST)

        transaction = PaymentTransaction.create_transaction(order, transaction_id, amount, payment_method)
        return Response(PaymentTransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)

class PaymentTransactionUpdateView(generics.UpdateAPIView):
    """Update transaction status"""
    queryset = PaymentTransaction.objects.all()
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAdminUser]

class PaymentTransactionDeleteView(generics.DestroyAPIView):
    """Delete a transaction (Admin Only)"""
    queryset = PaymentTransaction.objects.all()
    permission_classes = [IsAdminUser]
