from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db import models
import logging

from class_management.models import (
    ClassPurchase, ClassInstallment, ClassBundleConfig, ClassBundle, ClassBundleFile, ExpressClass
)
from class_management.serializers import (
    ClassPurchaseSerializer, ClassInstallmentSerializer,
    ClassBundleConfigSerializer, ClassBundleSerializer,
    AdminCreateClassBundleSerializer, AdminConfigureInstallmentsSerializer,
    ExpressClassSerializer, ExpressClassCreateSerializer,
    ExpressClassScopeReviewSerializer, ExpressClassAssignWriterSerializer
)
from class_management.services.class_purchases import handle_purchase_request
from class_management.services.pricing import get_class_price, InvalidPricingError
from class_management.services.class_bundle_admin import ClassBundleAdminService
from class_management.services.class_payment_processor import ClassPaymentProcessor
from class_management.services.class_communication import ClassBundleCommunicationService
from class_management.services.class_tickets import ClassBundleTicketService
from websites.models import Website
from communications.models import CommRole

logger = logging.getLogger(__name__)


class ClassBundleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing class bundles.
    Clients can view their bundles, admins can create and manage all bundles.
    """
    queryset = ClassBundle.objects.select_related('client', 'website', 'config', 'created_by_admin', 'assigned_writer').prefetch_related('installments', 'files')
    serializer_class = ClassBundleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter bundles based on user role."""
        user = self.request.user
        if user.is_staff:
            return self.queryset.all()
        # Clients see their bundles, writers see assigned bundles
        return self.queryset.filter(
            models.Q(client=user) | models.Q(assigned_writer=user)
        ).distinct()

    def get_website(self):
        """Get website from request."""
        domain = self.request.get_host()
        try:
            return Website.objects.get(domain=domain)
        except Website.DoesNotExist:
            return None

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def pay_deposit(self, request, pk=None):
        """
        Process deposit payment for a class bundle.
        
        Request body:
        {
            "payment_method": "wallet" | "stripe" | "manual",
            "discount_code": "optional_discount_code"
        }
        """
        bundle = self.get_object()
        
        # Validate client owns the bundle
        if bundle.client != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You do not have permission to pay for this bundle.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        payment_method = request.data.get('payment_method', 'wallet')
        discount_code = request.data.get('discount_code')
        
        try:
            payment = ClassPaymentProcessor.process_deposit_payment(
                bundle=bundle,
                client=request.user,
                payment_method=payment_method,
                discount_code=discount_code
            )
            
            return Response({
                'status': 'success',
                'payment_id': payment.id,
                'payment_status': payment.status,
                'bundle_id': bundle.id,
                'deposit_paid': float(bundle.deposit_paid),
                'message': 'Deposit payment processed successfully.'
            }, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception(f"Error processing deposit payment: {e}")
            return Response(
                {'error': 'An error occurred processing the payment.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def create_manual(self, request):
        """
        Admin endpoint to create a class bundle with manual pricing.
        
        Request body: See AdminCreateClassBundleSerializer
        """
        website = self.get_website()
        if not website:
            return Response(
                {'error': 'Website not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = AdminCreateClassBundleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            client = User.objects.get(id=data['client_id'])
        except Exception:
            return Response(
                {'error': 'Client not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            bundle = ClassBundleAdminService.create_manual_bundle(
                client=client,
                website=website,
                admin_user=request.user,
                total_price=data['total_price'],
                number_of_classes=data['number_of_classes'],
                deposit_required=data.get('deposit_required', 0),
                installments_enabled=data.get('installments_enabled', False),
                installment_count=data.get('installment_count'),
                duration=data.get('duration'),
                level=data.get('level'),
                bundle_size=data.get('bundle_size'),
                start_date=data.get('start_date'),
                end_date=data.get('end_date'),
                discount_code=data.get('discount_code'),
                discount_id=data.get('discount_id'),
            )
            
            return Response(
                ClassBundleSerializer(bundle).data,
                status=status.HTTP_201_CREATED
            )
            
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def configure_installments(self, request, pk=None):
        """
        Admin endpoint to configure installments for a bundle.
        
        Request body: See AdminConfigureInstallmentsSerializer
        """
        bundle = self.get_object()
        
        serializer = AdminConfigureInstallmentsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            bundle = ClassBundleAdminService.configure_installments(
                bundle=bundle,
                admin_user=request.user,
                installment_count=data['installment_count'],
                interval_weeks=data.get('interval_weeks', 2),
                amounts=data.get('amounts'),
            )
            
            return Response(
                ClassBundleSerializer(bundle).data,
                status=status.HTTP_200_OK
            )
            
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def create_thread(self, request, pk=None):
        """
        Create a communication thread for this class bundle.
        
        Request body:
        {
            "recipient_id": 123,
            "subject": "Optional subject",
            "initial_message": "Optional initial message"
        }
        """
        bundle = self.get_object()
        
        # Validate user has access
        if not ClassBundleCommunicationService.can_access_bundle_communication(request.user, bundle):
            return Response(
                {'error': 'You do not have permission to create threads for this bundle.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        recipient_id = request.data.get('recipient_id')
        if not recipient_id:
            return Response(
                {'error': 'recipient_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            recipient = User.objects.get(id=recipient_id)
        except Exception:
            return Response(
                {'error': 'Recipient not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            thread = ClassBundleCommunicationService.create_thread_for_bundle(
                bundle=bundle,
                created_by=request.user,
                recipient=recipient,
                subject=request.data.get('subject'),
                initial_message=request.data.get('initial_message')
            )
            
            from communications.serializers import CommunicationThreadSerializer
            return Response(
                CommunicationThreadSerializer(thread).data,
                status=status.HTTP_201_CREATED
            )
        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def create_ticket(self, request, pk=None):
        """
        Create a support ticket for this class bundle.
        
        Request body:
        {
            "title": "Ticket title",
            "description": "Ticket description",
            "priority": "low|medium|high|critical",
            "category": "general|payment|technical|feedback|order|other"
        }
        """
        bundle = self.get_object()
        
        # Validate user can create ticket
        if bundle.client != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Only the client or staff can create tickets.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            ticket = ClassBundleTicketService.create_ticket_for_bundle(
                bundle=bundle,
                created_by=request.user,
                title=request.data.get('title'),
                description=request.data.get('description'),
                priority=request.data.get('priority', 'medium'),
                category=request.data.get('category', 'general')
            )
            
            from tickets.serializers import TicketSerializer
            return Response(
                TicketSerializer(ticket).data,
                status=status.HTTP_201_CREATED
            )
        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_file(self, request, pk=None):
        """
        Upload a file for this class bundle.
        
        Request: multipart/form-data
        {
            "file": <file>,
            "description": "Optional description"
        }
        """
        bundle = self.get_object()
        
        # Validate user has access
        if not ClassBundleCommunicationService.can_access_bundle_communication(request.user, bundle):
            return Response(
                {'error': 'You do not have permission to upload files for this bundle.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if 'file' not in request.FILES:
            return Response(
                {'error': 'File is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES['file']
        description = request.data.get('description', '')
        
        # Create file record
        bundle_file = ClassBundleFile.objects.create(
            class_bundle=bundle,
            uploaded_by=request.user,
            file=file,
            file_name=file.name,
            file_size=file.size,
            description=description,
            is_visible_to_client=True,
            is_visible_to_writer=True
        )
        
        return Response({
            'id': bundle_file.id,
            'file_name': bundle_file.file_name,
            'file_size': bundle_file.file_size,
            'uploaded_by': bundle_file.uploaded_by.id,
            'uploaded_at': bundle_file.uploaded_at,
            'message': 'File uploaded successfully.'
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def threads(self, request, pk=None):
        """Get all communication threads for this bundle."""
        bundle = self.get_object()
        
        if not ClassBundleCommunicationService.can_access_bundle_communication(request.user, bundle):
            return Response(
                {'error': 'You do not have access to this bundle.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        threads = ClassBundleCommunicationService.get_threads_for_bundle(bundle, request.user)
        from communications.serializers import CommunicationThreadSerializer
        return Response(
            CommunicationThreadSerializer(threads, many=True).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def tickets(self, request, pk=None):
        """Get all support tickets for this bundle."""
        bundle = self.get_object()
        
        if not ClassBundleCommunicationService.can_access_bundle_communication(request.user, bundle):
            return Response(
                {'error': 'You do not have access to this bundle.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        tickets = ClassBundleTicketService.get_tickets_for_bundle(bundle, request.user)
        from tickets.serializers import TicketSerializer
        return Response(
            TicketSerializer(tickets, many=True).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def files(self, request, pk=None):
        """Get all files for this bundle."""
        bundle = self.get_object()
        
        if not ClassBundleCommunicationService.can_access_bundle_communication(request.user, bundle):
            return Response(
                {'error': 'You do not have access to this bundle.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Filter files based on visibility
        files = bundle.files.all()
        if request.user == bundle.client:
            files = files.filter(is_visible_to_client=True)
        elif request.user == bundle.assigned_writer:
            files = files.filter(is_visible_to_writer=True)
        elif not request.user.is_staff:
            # Non-staff users only see files visible to them
            files = files.none()
        
        return Response([
            {
                'id': f.id,
                'file_name': f.file_name,
                'file_size': f.file_size,
                'description': f.description,
                'uploaded_by': f.uploaded_by.id,
                'uploaded_at': f.uploaded_at,
                'file_url': f.file.url if f.file else None
            }
            for f in files
        ], status=status.HTTP_200_OK)


class ClassPurchaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing class purchase records.
    """
    queryset = ClassPurchase.objects.select_related('client', 'bundle', 'website', 'payment_record')
    serializer_class = ClassPurchaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter purchases based on user role."""
        user = self.request.user
        if user.is_staff:
            return self.queryset.all()
        return self.queryset.filter(client=user)

    
class ClassInstallmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling class installment records.
    """
    queryset = ClassInstallment.objects.select_related('class_bundle', 'paid_by', 'payment_record')
    serializer_class = ClassInstallmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return installments filtered by user role.
        """
        user = self.request.user
        if user.is_staff:
            return self.queryset.all()
        return self.queryset.filter(class_bundle__client=user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def pay_installment(self, request, pk=None):
        """
        Process payment for a specific installment.
        
        Request body:
        {
            "payment_method": "wallet" | "stripe" | "manual",
            "discount_code": "optional_discount_code"
        }
        """
        installment = self.get_object()
        
        # Validate client owns the bundle
        if installment.class_bundle.client != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You do not have permission to pay for this installment.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        payment_method = request.data.get('payment_method', 'wallet')
        discount_code = request.data.get('discount_code')
        
        try:
            payment = ClassPaymentProcessor.process_installment_payment(
                installment=installment,
                client=request.user,
                payment_method=payment_method,
                discount_code=discount_code
            )
            
            return Response({
                'status': 'success',
                'payment_id': payment.id,
                'payment_status': payment.status,
                'installment_id': installment.id,
                'amount': float(payment.amount),
                'message': 'Installment payment processed successfully.'
            }, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception(f"Error processing installment payment: {e}")
            return Response(
                {'error': 'An error occurred processing the payment.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    
class ClassBundleConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling class bundle pricing configurations.
    Only admin users can modify these configurations.
    """
    queryset = ClassBundleConfig.objects.all()
    serializer_class = ClassBundleConfigSerializer
    permission_classes = [IsAdminUser]

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
            website = self.get_website()
            price = get_class_price(program, duration, bundle_size, website)
            return Response({'price': str(price)}, status=200)
        except InvalidPricingError as e:
            return Response({'detail': str(e)}, status=404)


class ExpressClassViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing express classes (single class requests).
    Clients can create inquiries, admins review scope, set price, assign writers.
    """
    queryset = ExpressClass.objects.select_related('client', 'website', 'assigned_writer', 'reviewed_by').all()
    serializer_class = ExpressClassSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter express classes based on user role."""
        user = self.request.user
        if user.is_staff:
            return self.queryset.all()
        # Clients see their own express classes
        return self.queryset.filter(client=user)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return ExpressClassCreateSerializer
        return ExpressClassSerializer
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def review_scope(self, request, pk=None):
        """
        Admin reviews the scope and sets the price.
        
        Request body:
        {
            "scope_review_notes": "Notes from scope review",
            "price": 500.00,
            "installments_needed": 3,
            "admin_notes": "Optional admin notes"
        }
        """
        express_class = self.get_object()
        
        if express_class.status != ExpressClass.INQUIRY and express_class.status != ExpressClass.SCOPE_REVIEW:
            return Response(
                {'error': 'Can only review scope for inquiry or scope_review status.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ExpressClassScopeReviewSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            express_class.scope_review_notes = data['scope_review_notes']
            express_class.price = data['price']
            express_class.installments_needed = data.get('installments_needed', 0)
            express_class.admin_notes = data.get('admin_notes', '')
            express_class.reviewed_by = request.user
            express_class.reviewed_at = timezone.now()
            express_class.status = ExpressClass.PRICED
            express_class.price_approved = True
            express_class.save()
            
            return Response(
                ExpressClassSerializer(express_class).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception(f"Error reviewing scope: {e}")
            return Response(
                {'error': 'An error occurred reviewing the scope.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def assign_writer(self, request, pk=None):
        """
        Admin assigns a writer to the express class.
        
        Request body:
        {
            "writer_id": 123,
            "admin_notes": "Optional notes"
        }
        """
        express_class = self.get_object()
        
        if express_class.status != ExpressClass.PRICED:
            return Response(
                {'error': 'Can only assign writer after price has been set.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ExpressClassAssignWriterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            writer = User.objects.get(id=data['writer_id'], role='writer')
            
            express_class.assigned_writer = writer
            express_class.status = ExpressClass.ASSIGNED
            if data.get('admin_notes'):
                express_class.admin_notes = (express_class.admin_notes or '') + '\n' + data['admin_notes']
            express_class.save()
            
            return Response(
                ExpressClassSerializer(express_class).data,
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'Writer not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception(f"Error assigning writer: {e}")
            return Response(
                {'error': 'An error occurred assigning the writer.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def start_progress(self, request, pk=None):
        """Mark express class as in progress."""
        express_class = self.get_object()
        
        if express_class.status != ExpressClass.ASSIGNED:
            return Response(
                {'error': 'Can only start progress for assigned classes.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        express_class.status = ExpressClass.IN_PROGRESS
        express_class.save()
        
        return Response(
            ExpressClassSerializer(express_class).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def complete(self, request, pk=None):
        """Mark express class as completed."""
        express_class = self.get_object()
        
        express_class.status = ExpressClass.COMPLETED
        express_class.is_complete = True
        express_class.save()
        
        return Response(
            ExpressClassSerializer(express_class).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def create_thread(self, request, pk=None):
        """
        Create a communication thread for this express class.
        
        Request body:
        {
            "recipient_id": 123,
            "subject": "Optional subject",
            "initial_message": "Optional initial message"
        }
        """
        express_class = self.get_object()
        
        # Validate user has access
        user = request.user
        can_create = (
            express_class.client == user or
            express_class.assigned_writer == user or
            user.is_staff
        )
        
        if not can_create:
            return Response(
                {'error': 'You do not have permission to create threads for this express class.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        recipient_id = request.data.get('recipient_id')
        if not recipient_id:
            return Response(
                {'error': 'recipient_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            recipient = User.objects.get(id=recipient_id)
            
            from django.contrib.contenttypes.models import ContentType
            from communications.models import CommunicationThread, CommunicationMessage
            
            content_type = ContentType.objects.get_for_model(ExpressClass)
            
            # Determine sender and recipient roles
            sender_role = CommRole.CLIENT if user.role == 'client' else CommRole.ADMIN
            if user.role == 'writer':
                sender_role = CommRole.WRITER
            elif user.role == 'support':
                sender_role = CommRole.SUPPORT
            elif user.role == 'editor':
                sender_role = CommRole.EDITOR
            elif user.is_superuser:
                sender_role = CommRole.SUPERADMIN
            
            recipient_role = CommRole.CLIENT if recipient.role == 'client' else CommRole.ADMIN
            if recipient.role == 'writer':
                recipient_role = CommRole.WRITER
            elif recipient.role == 'support':
                recipient_role = CommRole.SUPPORT
            elif recipient.role == 'editor':
                recipient_role = CommRole.EDITOR
            elif recipient.is_superuser:
                recipient_role = CommRole.SUPERADMIN
            
            # Create thread - use 'class_bundle' or 'custom' for express classes
            thread = CommunicationThread.objects.create(
                website=express_class.website,
                thread_type='class_bundle',  # Use existing thread type for class-related threads
                order=None,
                special_order=None,
                content_type=content_type,
                object_id=express_class.id,
                subject=request.data.get('subject') or f"Express Class #{express_class.id} Communication",
                sender_role=sender_role,
                recipient_role=recipient_role,
                is_active=True,
            )
            
            # Add participants
            participants = [user, recipient, express_class.client]
            if express_class.assigned_writer:
                participants.append(express_class.assigned_writer)
            thread.participants.add(*set(participants))
            
            # Add initial message if provided
            if request.data.get('initial_message'):
                CommunicationMessage.objects.create(
                    thread=thread,
                    sender=user,
                    recipient=recipient,
                    sender_role=sender_role,
                    message=request.data.get('initial_message'),
                    message_type='text'
                )
            
            return Response(
                {'thread_id': thread.id, 'message': 'Thread created successfully.'},
                status=status.HTTP_201_CREATED
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'Recipient not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception(f"Error creating thread: {e}")
            return Response(
                {'error': 'An error occurred creating the thread.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def threads(self, request, pk=None):
        """Get all communication threads for this express class."""
        express_class = self.get_object()
        
        # Validate user has access
        user = request.user
        can_view = (
            express_class.client == user or
            express_class.assigned_writer == user or
            user.is_staff
        )
        
        if not can_view:
            return Response(
                {'error': 'You do not have permission to view threads for this express class.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        threads = express_class.message_threads.all()
        from communications.serializers import CommunicationThreadSerializer
        serializer = CommunicationThreadSerializer(threads, many=True, context={'request': request})
        
        return Response(serializer.data, status=status.HTTP_200_OK)
