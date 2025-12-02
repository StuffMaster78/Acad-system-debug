"""
Feedback System Serializers
"""
from rest_framework import serializers
from writer_management.models.feedback import Feedback, FeedbackHistory


class FeedbackSerializer(serializers.ModelSerializer):
    """Serializer for feedback."""
    from_user_email = serializers.CharField(source='from_user.email', read_only=True)
    to_user_email = serializers.CharField(source='to_user.email', read_only=True)
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    order_topic = serializers.CharField(source='order.topic', read_only=True)
    
    class Meta:
        model = Feedback
        fields = [
            'id',
            'website',
            'order',
            'order_id',
            'order_topic',
            'feedback_type',
            'from_user',
            'from_user_email',
            'to_user',
            'to_user_email',
            'overall_rating',
            'quality_rating',
            'communication_rating',
            'timeliness_rating',
            'professionalism_rating',
            'strengths',
            'areas_for_improvement',
            'specific_feedback',
            'feedback_points',
            'is_public',
            'is_anonymous',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'website', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create feedback."""
        request = self.context.get('request')
        if request and request.user:
            validated_data['from_user'] = request.user
            validated_data['website'] = request.user.website
            
            # Recalculate feedback history after creation
            if validated_data.get('to_user'):
                self._recalculate_history(validated_data['to_user'], validated_data['website'])
        
        return super().create(validated_data)
    
    def _recalculate_history(self, user, website):
        """Recalculate feedback history for user."""
        try:
            history = FeedbackHistory.objects.get(user=user, website=website)
            history.recalculate()
        except FeedbackHistory.DoesNotExist:
            FeedbackHistory.objects.create(user=user, website=website).recalculate()


class FeedbackCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating feedback."""
    
    class Meta:
        model = Feedback
        fields = [
            'order',
            'feedback_type',
            'to_user',
            'overall_rating',
            'quality_rating',
            'communication_rating',
            'timeliness_rating',
            'professionalism_rating',
            'strengths',
            'areas_for_improvement',
            'specific_feedback',
            'feedback_points',
            'is_public',
            'is_anonymous',
        ]
    
    def validate(self, attrs):
        """Validate feedback data."""
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("User not found")
        
        # Validate feedback type matches user roles
        feedback_type = attrs.get('feedback_type')
        from_user = request.user
        to_user = attrs.get('to_user')
        
        if not to_user:
            raise serializers.ValidationError("to_user is required")
        
        valid_combinations = {
            'editor_to_writer': (from_user.role == 'editor', to_user.role == 'writer'),
            'client_to_writer': (from_user.role == 'client', to_user.role == 'writer'),
            'client_to_editor': (from_user.role == 'client', to_user.role == 'editor'),
            'writer_to_client': (from_user.role == 'writer', to_user.role == 'client'),
        }
        
        if feedback_type not in valid_combinations:
            raise serializers.ValidationError(f"Invalid feedback type: {feedback_type}")
        
        from_valid, to_valid = valid_combinations[feedback_type]
        if not from_valid or not to_valid:
            raise serializers.ValidationError(f"Invalid user roles for feedback type {feedback_type}")
        
        return attrs


class FeedbackHistorySerializer(serializers.ModelSerializer):
    """Serializer for feedback history."""
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = FeedbackHistory
        fields = [
            'id',
            'user',
            'user_email',
            'website',
            'total_feedbacks',
            'average_rating',
            'average_quality_rating',
            'average_communication_rating',
            'average_timeliness_rating',
            'editor_feedbacks_count',
            'client_feedbacks_count',
            'last_30_days_rating',
            'last_90_days_rating',
            'last_calculated_at',
        ]
        read_only_fields = '__all__'

