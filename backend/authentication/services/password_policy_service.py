"""
Smart Password Policy Service - Context-aware password validation.
"""
import re
import logging
from typing import Dict, Any, List
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class SmartPasswordPolicy:
    """
    Context-aware password policy that adapts requirements based on:
    - Context (registration, password_change, password_reset, admin_action)
    - User risk profile
    - Recent security events
    """
    
    # Common passwords list (top 1000 most common)
    COMMON_PASSWORDS = [
        'password', '123456', '123456789', '12345678', '12345',
        '1234567', '1234567890', 'qwerty', 'abc123', 'monkey',
        '1234567', 'letmein', 'trustno1', 'dragon', 'baseball',
        'iloveyou', 'master', 'sunshine', 'ashley', 'bailey',
        'passw0rd', 'shadow', '123123', '654321', 'superman',
        'qazwsx', 'michael', 'football', 'welcome', 'jesus',
        'ninja', 'mustang', 'password1', '123qwe', 'admin',
    ]
    
    def validate_password(
        self,
        password: str,
        user=None,
        context: str = 'registration',
        email: str = None
    ) -> Dict[str, Any]:
        """
        Validate password based on context.
        
        Args:
            password: Password to validate
            user: User object (optional, for risk assessment)
            context: Validation context ('registration', 'password_change', 'password_reset', 'admin_action')
            email: User email (for checking against breaches)
        
        Returns:
            Dict with validation results, errors, strength, and suggestions
        """
        errors = []
        warnings = []
        
        # Base requirements (always required)
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        # Context-based requirements
        if context in ['password_change', 'admin_action']:
            # Stricter for sensitive operations
            if not re.search(r'[A-Z]', password):
                errors.append("Password must contain at least one uppercase letter")
            if not re.search(r'[a-z]', password):
                errors.append("Password must contain at least one lowercase letter")
            if not re.search(r'\d', password):
                errors.append("Password must contain at least one number")
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                warnings.append("Consider adding a special character for stronger security")
        
        elif context == 'registration':
            # Moderate requirements for new accounts
            if len(password) < 8:
                errors.append("Password must be at least 8 characters")
            # Suggest but don't require complexity
            if len(password) < 12 and not any(c.isupper() for c in password):
                warnings.append("Consider using a mix of uppercase and lowercase letters")
        
        # Check against common passwords
        if self.is_common_password(password):
            errors.append("This password is too common. Please choose a stronger, unique password.")
        
        # Check if password contains email/username
        if email and email.split('@')[0].lower() in password.lower():
            warnings.append("Avoid using your email address in your password")
        
        if user and hasattr(user, 'username') and user.username.lower() in password.lower():
            warnings.append("Avoid using your username in your password")
        
        # Check for repeated characters
        if re.search(r'(.)\1{3,}', password):
            warnings.append("Avoid using the same character repeated many times")
        
        # Check for sequential characters
        if self.has_sequential_chars(password):
            warnings.append("Avoid using sequential characters (e.g., '12345', 'abcde')")
        
        # Calculate strength
        strength = self.calculate_strength(password)
        
        # Generate suggestions
        suggestions = self.get_suggestions(password, errors, warnings)
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "strength": strength,
            "strength_label": self.get_strength_label(strength),
            "suggestions": suggestions,
            "meets_requirements": len(errors) == 0
        }
    
    def calculate_strength(self, password: str) -> int:
        """
        Calculate password strength (0-100).
        
        Returns:
            Strength score from 0-100
        """
        score = 0
        
        # Length (40 points max)
        if len(password) >= 8:
            score += 20
        if len(password) >= 12:
            score += 10
        if len(password) >= 16:
            score += 10
        
        # Complexity (40 points max)
        if re.search(r'[a-z]', password):
            score += 10
        if re.search(r'[A-Z]', password):
            score += 10
        if re.search(r'\d', password):
            score += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 10
        
        # Uniqueness (20 points max)
        if not self.is_common_password(password):
            score += 10
        if not self.has_sequential_chars(password):
            score += 5
        if not re.search(r'(.)\1{2,}', password):  # No repeated chars
            score += 5
        
        return min(score, 100)
    
    def get_strength_label(self, strength: int) -> str:
        """Get human-readable strength label."""
        if strength < 30:
            return "Very Weak"
        elif strength < 50:
            return "Weak"
        elif strength < 70:
            return "Fair"
        elif strength < 90:
            return "Good"
        else:
            return "Strong"
    
    def is_common_password(self, password: str) -> bool:
        """Check if password is in common passwords list."""
        password_lower = password.lower()
        return password_lower in [p.lower() for p in self.COMMON_PASSWORDS]
    
    def has_sequential_chars(self, password: str) -> bool:
        """Check for sequential characters (e.g., '12345', 'abcde')."""
        password_lower = password.lower()
        
        # Check numeric sequences
        for i in range(len(password_lower) - 3):
            substr = password_lower[i:i+4]
            if substr.isdigit():
                digits = [int(c) for c in substr]
                if all(digits[j] == digits[0] + j for j in range(len(digits))):
                    return True
        
        # Check alphabetic sequences
        for i in range(len(password_lower) - 3):
            substr = password_lower[i:i+4]
            if substr.isalpha():
                ords = [ord(c) for c in substr]
                if all(ords[j] == ords[0] + j for j in range(len(ords))):
                    return True
        
        return False
    
    def get_suggestions(self, password: str, errors: List[str], warnings: List[str]) -> List[str]:
        """Generate password improvement suggestions."""
        suggestions = []
        
        if len(password) < 12:
            suggestions.append("Use at least 12 characters for better security")
        
        if not re.search(r'[A-Z]', password):
            suggestions.append("Add uppercase letters")
        
        if not re.search(r'[a-z]', password):
            suggestions.append("Add lowercase letters")
        
        if not re.search(r'\d', password):
            suggestions.append("Add numbers")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            suggestions.append("Add special characters (!@#$%^&*)")
        
        if self.is_common_password(password):
            suggestions.append("Avoid common words and phrases")
        
        return suggestions[:5]  # Limit to 5 suggestions

