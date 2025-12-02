"""
Writer Portfolio Serializers
"""
from rest_framework import serializers
from writer_management.models.portfolio import WriterPortfolio, PortfolioSample


class PortfolioSampleSerializer(serializers.ModelSerializer):
    """Serializer for portfolio samples."""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    type_of_work_name = serializers.CharField(source='type_of_work.name', read_only=True)
    writer_email = serializers.CharField(source='writer.email', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = PortfolioSample
        fields = [
            'id',
            'website',
            'writer',
            'writer_email',
            'title',
            'description',
            'source_order',
            'file',
            'file_url',
            'content_preview',
            'subject',
            'subject_name',
            'type_of_work',
            'type_of_work_name',
            'is_anonymized',
            'is_featured',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'website', 'writer', 'created_at', 'updated_at']
    
    def get_file_url(self, obj):
        """Get file URL if file exists."""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
    def create(self, validated_data):
        """Create portfolio sample."""
        request = self.context.get('request')
        if request and request.user:
            validated_data['writer'] = request.user
            validated_data['website'] = request.user.website
        return super().create(validated_data)


class WriterPortfolioSerializer(serializers.ModelSerializer):
    """Serializer for writer portfolio."""
    writer_email = serializers.CharField(source='writer.email', read_only=True)
    specialties_names = serializers.SerializerMethodField()
    sample_works = PortfolioSampleSerializer(many=True, read_only=True)
    can_view = serializers.SerializerMethodField()
    
    class Meta:
        model = WriterPortfolio
        fields = [
            'id',
            'writer',
            'writer_email',
            'website',
            'is_enabled',
            'visibility',
            'bio',
            'specialties',
            'specialties_names',
            'years_of_experience',
            'education',
            'certifications',
            'sample_works',
            'total_orders_completed',
            'average_rating',
            'on_time_delivery_rate',
            'show_contact_info',
            'show_order_history',
            'show_earnings',
            'created_at',
            'updated_at',
            'can_view',
        ]
        read_only_fields = [
            'id', 'writer', 'website', 'total_orders_completed',
            'average_rating', 'on_time_delivery_rate', 'created_at', 'updated_at'
        ]
    
    def get_specialties_names(self, obj):
        """Get names of specialties."""
        return [subject.name for subject in obj.specialties.all()]
    
    def get_can_view(self, obj):
        """Check if current user can view this portfolio."""
        request = self.context.get('request')
        if not request or not request.user:
            return False
        return obj.can_view(request.user)
    
    def create(self, validated_data):
        """Create portfolio for current user."""
        request = self.context.get('request')
        if request and request.user:
            validated_data['writer'] = request.user
            validated_data['website'] = request.user.website
        return super().create(validated_data)


class WriterPortfolioUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating portfolio."""
    
    class Meta:
        model = WriterPortfolio
        fields = [
            'is_enabled',
            'visibility',
            'bio',
            'specialties',
            'years_of_experience',
            'education',
            'certifications',
            'show_contact_info',
            'show_order_history',
            'show_earnings',
        ]


class PortfolioSampleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating portfolio samples."""
    
    class Meta:
        model = PortfolioSample
        fields = [
            'title',
            'description',
            'source_order',
            'file',
            'content_preview',
            'subject',
            'type_of_work',
            'is_anonymized',
            'is_featured',
        ]

