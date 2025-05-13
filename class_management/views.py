from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.utils import timezone
from django.utils.timezone import timedelta
from rest_framework.response import Response
from class_management.models import ClassPurchase, ClassInstallment, ClassBundleConfig
from class_management.serializers import (
    ClassPurchaseSerializer, ClassInstallmentSerializer,
    ClassBundleConfigSerializer
)
from class_management.services.class_purchases import handle_purchase_request
from class_management.services.pricing import get_class_price, InvalidPricingError
from websites.models import Website
from rest_framework.permissions import IsAuthenticated, IsAdminUser

class ClassPurchaseViewSet(viewsets.ModelViewSet):
    queryset = ClassPurchase.objects.all()
    serializer_class = ClassPurchaseSerializer
    lookup_field = 'id'

    def get_website(self):
        domain = self.request.get_host()
        return Website.objects.get(domain=domain)

    def perform_create(self, serializer):
        website = self.get_website()
        purchase = handle_purchase_request(
            user=self.request.user,
            data=self.request.data,
            website=website
        )
        serializer.instance = purchase

    @action(detail=True, methods=['post'])
    def pay_installment(self, request, pk=None):
        from class_management.services.installments import charge_installment
        purchase = self.get_object()
        installment = purchase.installments.filter(paid=False).first()

        if not installment:
            return Response(
                {"detail": "All installments are already paid."},
                status=status.HTTP_400_BAD_REQUEST
            )

        charge_installment(self.request.user, installment)
        return Response({"detail": "Installment paid."})

    
class ClassInstallmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling class installment records.
    """
    queryset = ClassInstallment.objects.all()
    serializer_class = ClassInstallmentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Custom logic during installment creation.
        You can auto-set installment due date, charge wallet, etc.
        """
        if not serializer.validated_data.get('due_date'):
            # Set due date 2 weeks from now
            serializer.validated_data['due_date'] = timezone.now() + timedelta(weeks=2)
        super().perform_create(serializer)
    
    def get_queryset(self):
        """
        Return only the installments for the currently authenticated user.
        """
        return self.queryset.filter(purchase__client=self.request.user)

    
class ClassBundleConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling class bundle pricing configurations.
    Only admin users can modify these configurations.
    """
    queryset = ClassBundleConfig.objects.all()
    serializer_class = ClassBundleConfigSerializer
    permission_classes = [IsAdminUser]  # Only admins can modify class bundle configurations

    def get_website(self):
        domain = self.request.get_host()
        return Website.objects.get(domain=domain)

    def get_queryset(self):
        """
        Filter the configurations by the current website.
        """
        website = self.get_website()
        return self.queryset.filter(website=website)

    @action(detail=False, methods=['get'])
    def get_class_price(self, request):
        """
        Custom action to retrieve class pricing for a specific program, duration, and bundle size.
        """
        program = request.query_params.get('program')
        duration = request.query_params.get('duration')
        bundle_size = int(request.query_params.get('bundle_size', 1))

        if not program or not duration:
            return Response({'detail': 'Program and duration are required.'}, status=400)

        try:
            price = get_class_price(program, duration, bundle_size)
            return Response({'price': str(price)}, status=200)
        except InvalidPricingError as e:
            return Response({'detail': str(e)}, status=404)
