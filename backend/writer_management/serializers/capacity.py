"""
Writer Capacity & Editor Workload Serializers
"""
from rest_framework import serializers
from writer_management.models.capacity import WriterCapacity, EditorWorkload


class WriterCapacitySerializer(serializers.ModelSerializer):
    """Serializer for writer capacity settings."""
    preferred_subjects_names = serializers.SerializerMethodField()
    preferred_types_of_work_names = serializers.SerializerMethodField()
    can_accept_order = serializers.SerializerMethodField()
    capacity_status = serializers.SerializerMethodField()
    
    class Meta:
        model = WriterCapacity
        fields = [
            'id',
            'writer',
            'website',
            'max_active_orders',
            'current_active_orders',
            'is_available',
            'availability_message',
            'preferred_subjects',
            'preferred_subjects_names',
            'preferred_types_of_work',
            'preferred_types_of_work_names',
            'blackout_dates',
            'preferred_deadline_buffer_days',
            'max_orders_per_day',
            'auto_accept_orders',
            'auto_accept_preferred_only',
            'created_at',
            'updated_at',
            'can_accept_order',
            'capacity_status',
        ]
        read_only_fields = [
            'id', 'writer', 'website', 'current_active_orders',
            'created_at', 'updated_at', 'can_accept_order', 'capacity_status'
        ]
    
    def get_preferred_subjects_names(self, obj):
        """Get names of preferred subjects."""
        return [subject.name for subject in obj.preferred_subjects.all()]
    
    def get_preferred_types_of_work_names(self, obj):
        """Get names of preferred types of work."""
        return [type_of_work.name for type_of_work in obj.preferred_types_of_work.all()]
    
    def get_can_accept_order(self, obj):
        """Check if writer can accept a new order."""
        can_accept, reason = obj.can_accept_order()
        return can_accept
    
    def get_capacity_status(self, obj):
        """Get capacity status message."""
        can_accept, reason = obj.can_accept_order()
        return {
            'can_accept': can_accept,
            'reason': reason,
            'utilization': f"{obj.current_active_orders}/{obj.max_active_orders}",
            'utilization_percent': (obj.current_active_orders / obj.max_active_orders * 100) if obj.max_active_orders > 0 else 0,
        }
    
    def create(self, validated_data):
        """Create capacity settings for current user."""
        request = self.context.get('request')
        if request and request.user:
            validated_data['writer'] = request.user
            validated_data['website'] = request.user.website
        return super().create(validated_data)


class WriterCapacityUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating writer capacity."""
    
    class Meta:
        model = WriterCapacity
        fields = [
            'max_active_orders',
            'is_available',
            'availability_message',
            'preferred_subjects',
            'preferred_types_of_work',
            'blackout_dates',
            'preferred_deadline_buffer_days',
            'max_orders_per_day',
            'auto_accept_orders',
            'auto_accept_preferred_only',
        ]


class EditorWorkloadSerializer(serializers.ModelSerializer):
    """Serializer for editor workload settings."""
    preferred_subjects_names = serializers.SerializerMethodField()
    preferred_types_of_work_names = serializers.SerializerMethodField()
    can_accept_task = serializers.SerializerMethodField()
    
    class Meta:
        model = EditorWorkload
        fields = [
            'id',
            'editor',
            'website',
            'max_active_tasks',
            'current_active_tasks',
            'is_available',
            'preferred_subjects',
            'preferred_subjects_names',
            'preferred_types_of_work',
            'preferred_types_of_work_names',
            'created_at',
            'updated_at',
            'can_accept_task',
        ]
        read_only_fields = [
            'id', 'editor', 'website', 'current_active_tasks',
            'created_at', 'updated_at', 'can_accept_task'
        ]
    
    def get_preferred_subjects_names(self, obj):
        """Get names of preferred subjects."""
        return [subject.name for subject in obj.preferred_subjects.all()]
    
    def get_preferred_types_of_work_names(self, obj):
        """Get names of preferred types of work."""
        return [type_of_work.name for type_of_work in obj.preferred_types_of_work.all()]
    
    def get_can_accept_task(self, obj):
        """Check if editor can accept a new task."""
        return obj.is_available and obj.current_active_tasks < obj.max_active_tasks
    
    def create(self, validated_data):
        """Create workload settings for current user."""
        request = self.context.get('request')
        if request and request.user:
            validated_data['editor'] = request.user
            validated_data['website'] = request.user.website
        return super().create(validated_data)

