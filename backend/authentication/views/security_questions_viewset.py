"""
Security Questions ViewSet
Handles security questions for account recovery.
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.exceptions import ValidationError

from authentication.models.security_questions import SecurityQuestion, UserSecurityQuestion
from authentication.services.security_questions_service import SecurityQuestionsService
from authentication.serializers import (
    SecurityQuestionSerializer, UserSecurityQuestionSerializer
)

logger = logging.getLogger(__name__)


class SecurityQuestionsViewSet(viewsets.ViewSet):
    """
    ViewSet for security questions.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='available', permission_classes=[AllowAny])
    def get_available_questions(self, request):
        """Get available security questions."""
        service = SecurityQuestionsService(request.user if request.user.is_authenticated else None)
        questions = service.get_available_questions()
        serializer = SecurityQuestionSerializer(questions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='my-questions')
    def get_my_questions(self, request):
        """Get user's security questions (without answers)."""
        service = SecurityQuestionsService(request.user)
        questions = service.get_user_questions()
        serializer = UserSecurityQuestionSerializer(questions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='set')
    def set_security_questions(self, request):
        """
        Set security questions for user.
        
        Request body:
        {
            "questions": [
                {"question_id": 1, "answer": "answer1"},
                {"custom_question": "What is your favorite color?", "answer": "blue"},
                ...
            ]
        }
        """
        questions_data = request.data.get('questions', [])
        
        if not questions_data:
            return Response(
                {'error': 'Questions data is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = SecurityQuestionsService(request.user)
        try:
            created_questions = service.set_security_questions(questions_data)
            serializer = UserSecurityQuestionSerializer(created_questions, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'], url_path='verify', permission_classes=[AllowAny])
    def verify_answers(self, request):
        """
        Verify security question answers (for account recovery).
        
        Request body:
        {
            "email": "user@example.com",
            "answers": [
                {"question_id": 1, "answer": "answer1"},
                {"question_id": 2, "answer": "answer2"},
                ...
            ]
        }
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        email = request.data.get('email')
        answers = request.data.get('answers', [])
        
        if not email or not answers:
            return Response(
                {'error': 'Email and answers are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        service = SecurityQuestionsService(user)
        
        if not service.can_use_for_recovery():
            return Response(
                {'error': 'Security questions not set up for this account'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            verified = service.verify_answers(answers)
            if verified:
                return Response({'verified': True, 'message': 'Answers verified successfully'})
            else:
                return Response(
                    {'verified': False, 'error': 'Incorrect answers'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['delete'], url_path='delete-all')
    def delete_all_questions(self, request):
        """Delete all security questions for user."""
        service = SecurityQuestionsService(request.user)
        service.delete_all_questions()
        return Response({'message': 'All security questions deleted'})

