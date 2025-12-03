"""
Security Questions Service
Manages security questions for account recovery.
"""
import logging
from typing import List, Optional
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from authentication.models.security_questions import SecurityQuestion, UserSecurityQuestion
from websites.utils import get_current_website

logger = logging.getLogger(__name__)


class SecurityQuestionsService:
    """
    Service for managing security questions.
    """
    
    MIN_QUESTIONS = 2
    MAX_QUESTIONS = 5
    
    def __init__(self, user, website=None):
        self.user = user
        self.website = website or get_current_website()
        if not self.website:
            from websites.models import Website
            self.website = Website.objects.filter(is_active=True).first()
    
    def get_available_questions(self) -> List[SecurityQuestion]:
        """Get available security questions."""
        return list(SecurityQuestion.objects.filter(is_active=True).order_by('question_text'))
    
    def get_user_questions(self) -> List[UserSecurityQuestion]:
        """Get user's security questions."""
        if not self.website:
            return []
        
        return list(UserSecurityQuestion.objects.filter(
            user=self.user,
            website=self.website,
            is_active=True
        ).select_related('question'))
    
    def set_security_questions(self, questions_data: List[dict]) -> List[UserSecurityQuestion]:
        """
        Set security questions for user.
        
        Args:
            questions_data: List of dicts with 'question_id' or 'custom_question' and 'answer'
        
        Returns:
            List of created UserSecurityQuestion instances
        """
        if not self.website:
            raise ValueError("Website context required")
        
        if len(questions_data) < self.MIN_QUESTIONS:
            raise ValidationError(f"At least {self.MIN_QUESTIONS} security questions are required")
        
        if len(questions_data) > self.MAX_QUESTIONS:
            raise ValidationError(f"Maximum {self.MAX_QUESTIONS} security questions allowed")
        
        # Deactivate existing questions
        UserSecurityQuestion.objects.filter(
            user=self.user,
            website=self.website
        ).update(is_active=False)
        
        created_questions = []
        question_ids_used = set()
        
        for q_data in questions_data:
            question_id = q_data.get('question_id')
            custom_question = q_data.get('custom_question', '').strip()
            answer = q_data.get('answer', '').strip()
            
            if not answer:
                raise ValidationError("Answer is required for all security questions")
            
            if not question_id and not custom_question:
                raise ValidationError("Either question_id or custom_question is required")
            
            # Validate answer length
            if len(answer) < 3:
                raise ValidationError("Answer must be at least 3 characters long")
            
            # Get or create question
            if question_id:
                if question_id in question_ids_used:
                    raise ValidationError("Duplicate questions are not allowed")
                question_ids_used.add(question_id)
                
                try:
                    question = SecurityQuestion.objects.get(id=question_id, is_active=True)
                except SecurityQuestion.DoesNotExist:
                    raise ValidationError(f"Invalid question ID: {question_id}")
            else:
                question = None
                if len(custom_question) < 10:
                    raise ValidationError("Custom question must be at least 10 characters long")
            
            # Create user security question
            user_question = UserSecurityQuestion.objects.create(
                user=self.user,
                website=self.website,
                question=question,
                custom_question=custom_question if custom_question else '',
                is_active=True
            )
            
            # Set encrypted answer
            user_question.set_answer(answer)
            user_question.save()
            
            created_questions.append(user_question)
        
        return created_questions
    
    def verify_answers(self, answers: List[dict]) -> bool:
        """
        Verify security question answers.
        
        Args:
            answers: List of dicts with 'question_id' and 'answer'
        
        Returns:
            True if all answers are correct
        """
        if not self.website:
            return False
        
        user_questions = self.get_user_questions()
        
        if len(answers) != len(user_questions):
            return False
        
        # Create a map of question IDs to user questions
        question_map = {q.question.id if q.question else None: q for q in user_questions}
        
        correct_count = 0
        for answer_data in answers:
            question_id = answer_data.get('question_id')
            answer = answer_data.get('answer', '').strip()
            
            user_question = question_map.get(question_id)
            if not user_question:
                continue
            
            if user_question.verify_answer(answer):
                correct_count += 1
        
        # Require all answers to be correct
        return correct_count == len(user_questions)
    
    def can_use_for_recovery(self) -> bool:
        """Check if user has enough security questions set up."""
        return len(self.get_user_questions()) >= self.MIN_QUESTIONS
    
    def delete_all_questions(self):
        """Delete all security questions for user."""
        if not self.website:
            return
        
        UserSecurityQuestion.objects.filter(
            user=self.user,
            website=self.website
        ).delete()

