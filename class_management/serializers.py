from rest_framework import serializers
from class_management.models import (
    ClassPurchase, ClassInstallment, ClassBundleConfig, ClassBundle, ClassBundleFile, ExpressClass
)
from websites.models import Website


class ClassInstallmentSerializer(serializers.ModelSerializer):
    payment_record_id = serializers.IntegerField(source='payment_record.id', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = ClassInstallment
        fields = (
            'id', 'class_bundle', 'amount', 'due_date', 'is_paid', 
            'paid_at', 'paid_by', 'payment_record', 'payment_record_id',
            'installment_number', 'created_at', 'is_overdue'
        )
        read_only_fields = ('payment_record', 'paid_at', 'created_at')

    def get_is_overdue(self, obj):
        """Check if installment is overdue."""
        if obj.is_paid or not obj.due_date:
            return False
        from django.utils import timezone
        return timezone.now().date() > obj.due_date

    def validate(self, data):
        """
        Validate installment data.
        """
        if data.get('amount', 0) <= 0:
            raise serializers.ValidationError("Installment amount must be greater than 0.")
        return data


class ClassBundleFileSerializer(serializers.ModelSerializer):
    """Serializer for class bundle file attachments."""
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ClassBundleFile
        fields = (
            'id', 'file_name', 'file_size', 'description',
            'uploaded_by', 'uploaded_by_username',
            'is_visible_to_client', 'is_visible_to_writer',
            'uploaded_at', 'file_url'
        )
        read_only_fields = ('uploaded_at',)
    
    def get_file_url(self, obj):
        """Get file URL."""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class ClassBundleSerializer(serializers.ModelSerializer):
    installments = ClassInstallmentSerializer(many=True, read_only=True)
    purchases = serializers.SerializerMethodField()
    files = ClassBundleFileSerializer(many=True, read_only=True)
    threads_count = serializers.SerializerMethodField()
    tickets_count = serializers.SerializerMethodField()
    has_deposit_paid = serializers.BooleanField(read_only=True)
    is_fully_paid = serializers.BooleanField(read_only=True)
    pricing_source_display = serializers.CharField(source='get_pricing_source_display', read_only=True)
    discount_code = serializers.CharField(source='discount.discount_code', read_only=True)
    discount_amount = serializers.SerializerMethodField()
    assigned_writer_username = serializers.CharField(source='assigned_writer.username', read_only=True)
    
    class Meta:
        model = ClassBundle
        fields = (
            'id', 'client', 'website', 'config', 'pricing_source', 'pricing_source_display',
            'duration', 'status', 'level', 'bundle_size', 'price_per_class',
            'number_of_classes', 'start_date', 'end_date',
            'total_price', 'original_price', 'discount', 'discount_code', 'discount_amount',
            'deposit_required', 'deposit_paid', 'balance_remaining',
            'installments_enabled', 'installment_count',
            'assigned_writer', 'assigned_writer_username',
            'created_by_admin', 'installments', 'purchases', 'files',
            'threads_count', 'tickets_count',
            'has_deposit_paid', 'is_fully_paid', 'is_complete',
            'created_at', 'completed_at'
        )
        read_only_fields = (
            'deposit_paid', 'balance_remaining', 'has_deposit_paid', 
            'is_fully_paid', 'created_at', 'completed_at'
        )
    
    def get_threads_count(self, obj):
        """Get count of communication threads."""
        return obj.message_threads.count()
    
    def get_tickets_count(self, obj):
        """Get count of support tickets."""
        return obj.support_tickets.count()
    
    def get_discount_amount(self, obj):
        """Calculate discount amount if discount applied."""
        if obj.discount and obj.original_price:
            return float(obj.original_price - obj.total_price)
        return None
    
    def get_purchases(self, obj):
        """Get purchase records for this bundle."""
        purchases = obj.purchases.all()[:5]  # Limit to recent purchases
        return [
            {
                'id': str(p.id),
                'payment_type': p.payment_type,
                'status': p.status,
                'price_locked': str(p.price_locked),
                'paid_at': p.paid_at,
            }
            for p in purchases
        ]


class ClassPurchaseSerializer(serializers.ModelSerializer):
    bundle_info = ClassBundleSerializer(source='bundle', read_only=True)
    payment_record_id = serializers.IntegerField(source='payment_record.id', read_only=True)

    class Meta:
        model = ClassPurchase
        fields = (
            'id', 'client', 'bundle', 'bundle_info', 'website', 
            'payment_record', 'payment_record_id', 'payment_type',
            'status', 'price_locked', 'paid_at', 'reference_id', 'created_at'
        )
        read_only_fields = ('payment_record', 'paid_at', 'created_at')


class ClassBundleConfigSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    
    class Meta:
        model = ClassBundleConfig
        fields = (
            'id', 'website', 'duration', 'level', 'bundle_size', 
            'price_per_class', 'total_price', 'is_active'
        )

    def validate_price_per_class(self, value):
        """
        Ensure the price per class is a valid value.
        """
        if value <= 0:
            raise serializers.ValidationError("Price per class must be greater than zero.")
        return value


class AdminCreateClassBundleSerializer(serializers.Serializer):
    """Serializer for admin to manually create class bundles."""
    client_id = serializers.IntegerField(help_text="Client user ID")
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Agreed price $X (original price before discount - discount will be applied if provided)"
    )
    number_of_classes = serializers.IntegerField(min_value=1)
    deposit_required = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, default=0,
        help_text="Deposit amount (after discount)"
    )
    installments_enabled = serializers.BooleanField(default=False)
    installment_count = serializers.IntegerField(min_value=1, required=False)
    duration = serializers.CharField(max_length=10, required=False, allow_blank=True)
    level = serializers.CharField(max_length=10, required=False, allow_blank=True)
    bundle_size = serializers.IntegerField(min_value=1, required=False)
    start_date = serializers.DateField(
        required=False, allow_null=True,
        help_text="Class start date (date A)"
    )
    end_date = serializers.DateField(
        required=False, allow_null=True,
        help_text="Class end date (date B)"
    )
    discount_code = serializers.CharField(
        max_length=50, required=False, allow_blank=True,
        help_text="Discount code to apply (admin sets discount)"
    )
    discount_id = serializers.IntegerField(
        required=False, allow_null=True,
        help_text="Discount ID to apply (alternative to discount_code)"
    )
    
    def validate(self, data):
        """Validate bundle creation data."""
        deposit = data.get('deposit_required', 0)
        total_price = data['total_price']
        
        if deposit < 0:
            raise serializers.ValidationError("Deposit cannot be negative.")
        if deposit > total_price:
            raise serializers.ValidationError("Deposit cannot exceed total price.")
        
        if data.get('installments_enabled'):
            if not data.get('installment_count'):
                raise serializers.ValidationError(
                    "installment_count is required when installments_enabled is True."
                )
            remaining = total_price - deposit
            if remaining <= 0:
                raise serializers.ValidationError(
                    "Cannot enable installments when deposit equals or exceeds total price."
                )
        
        return data


class AdminConfigureInstallmentsSerializer(serializers.Serializer):
    """Serializer for admin to configure installments."""
    installment_count = serializers.IntegerField(min_value=1)
    interval_weeks = serializers.IntegerField(min_value=1, default=2)
    amounts = serializers.ListField(
        child=serializers.DecimalField(max_digits=10, decimal_places=2),
        required=False,
        help_text="Optional: Specific amounts per installment (must sum to balance)"
    )
    
    def validate(self, data):
        """Validate installment configuration."""
        amounts = data.get('amounts')
        if amounts:
            count = data['installment_count']
            if len(amounts) != count:
                raise serializers.ValidationError(
                    f"Must provide exactly {count} installment amounts."
                )
            if any(a <= 0 for a in amounts):
                raise serializers.ValidationError(
                    "All installment amounts must be greater than zero."
                )
        return data


class ExpressClassSerializer(serializers.ModelSerializer):
    """Serializer for ExpressClass model."""
    client_username = serializers.CharField(source='client.username', read_only=True)
    client_email = serializers.CharField(source='client.email', read_only=True)
    assigned_writer_username = serializers.CharField(source='assigned_writer.username', read_only=True)
    website_name = serializers.CharField(source='website.name', read_only=True)
    reviewed_by_username = serializers.CharField(source='reviewed_by.username', read_only=True)
    threads_count = serializers.SerializerMethodField()
    tickets_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ExpressClass
        fields = (
            'id', 'client', 'client_username', 'client_email',
            'website', 'website_name',
            'assigned_writer', 'assigned_writer_username',
            'status', 'status_display',
            'start_date', 'end_date',
            'discipline', 'institution', 'course', 'academic_level',
            'number_of_discussion_posts', 'number_of_discussion_posts_replies',
            'number_of_assignments', 'number_of_exams', 'number_of_quizzes',
            'number_of_projects', 'number_of_presentations', 'number_of_papers',
            'total_workload_in_pages',
            'price', 'price_approved', 'installments_needed',
            'instructions',
            'school_login_link', 'school_login_username', 'school_login_password',
            'scope_review_notes', 'admin_notes',
            'reviewed_by', 'reviewed_by_username', 'reviewed_at',
            'threads_count', 'tickets_count',
            'is_complete', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at', 'reviewed_at')
    
    def get_threads_count(self, obj):
        """Get count of communication threads."""
        return obj.message_threads.count()
    
    def get_tickets_count(self, obj):
        """Get count of support tickets."""
        return obj.support_tickets.count()


class ExpressClassCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating express class (client inquiry)."""
    
    class Meta:
        model = ExpressClass
        fields = (
            'client', 'website', 'start_date', 'end_date',
            'discipline', 'institution', 'course', 'academic_level',
            'number_of_discussion_posts', 'number_of_discussion_posts_replies',
            'number_of_assignments', 'number_of_exams', 'number_of_quizzes',
            'number_of_projects', 'number_of_presentations', 'number_of_papers',
            'total_workload_in_pages', 'instructions',
            'school_login_link', 'school_login_username', 'school_login_password'
        )


class ExpressClassScopeReviewSerializer(serializers.Serializer):
    """Serializer for admin scope review."""
    scope_review_notes = serializers.CharField(required=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    installments_needed = serializers.IntegerField(min_value=0, required=False, default=0)
    admin_notes = serializers.CharField(required=False, allow_blank=True)


class ExpressClassAssignWriterSerializer(serializers.Serializer):
    """Serializer for assigning writer to express class."""
    writer_id = serializers.IntegerField(required=True)
    admin_notes = serializers.CharField(required=False, allow_blank=True)
