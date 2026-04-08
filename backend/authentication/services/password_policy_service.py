"""
Smart password policy service.

Provide context-aware password validation, feedback, and strength
scoring for registration, password changes, resets, and admin actions.
"""

import re
from typing import Any


class SmartPasswordPolicy:
    """
    Context-aware password policy.

    This policy adapts validation based on:
        - operation context
        - user-derived identifiers
        - common-password checks
        - predictable password patterns
    """

    class Context:
        REGISTRATION = "registration"
        PASSWORD_CHANGE = "password_change"
        PASSWORD_RESET = "password_reset"
        ADMIN_ACTION = "admin_action"

    COMMON_PASSWORDS = {
        "password",
        "123456",
        "123456789",
        "12345678",
        "12345",
        "1234567",
        "1234567890",
        "qwerty",
        "abc123",
        "monkey",
        "letmein",
        "trustno1",
        "dragon",
        "baseball",
        "iloveyou",
        "master",
        "sunshine",
        "ashley",
        "bailey",
        "passw0rd",
        "shadow",
        "123123",
        "654321",
        "superman",
        "qazwsx",
        "michael",
        "football",
        "welcome",
        "jesus",
        "ninja",
        "mustang",
        "password1",
        "123qwe",
        "admin",
    }

    SPECIAL_CHAR_PATTERN = r'[!@#$%^&*(),.?":{}|<>]'
    CONTEXTS = {
        Context.REGISTRATION,
        Context.PASSWORD_CHANGE,
        Context.PASSWORD_RESET,
        Context.ADMIN_ACTION,
    }

    def validate_password(
        self,
        password: str,
        user=None,
        context: str = Context.REGISTRATION,
        email: str | None = None,
        banned_fragments: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Validate a password for a given context.

        Args:
            password: Password to validate.
            user: Optional user object for personalized checks.
            context: Validation context.
            email: Optional email address.
            banned_fragments: Optional forbidden substrings.

        Returns:
            Validation result dictionary containing:
                - valid
                - errors
                - warnings
                - strength
                - strength_label
                - suggestions
                - meets_requirements
        """
        if context not in self.CONTEXTS:
            context = self.Context.REGISTRATION

        errors: list[str] = []
        warnings: list[str] = []

        normalized_password = password.strip()

        if not normalized_password:
            return {
                "valid": False,
                "errors": ["Password cannot be empty."],
                "warnings": [],
                "strength": 0,
                "strength_label": "Very Weak",
                "suggestions": ["Enter a password."],
                "meets_requirements": False,
            }

        self._apply_base_rules(
            password=normalized_password,
            errors=errors,
        )

        self._apply_context_rules(
            password=normalized_password,
            context=context,
            errors=errors,
            warnings=warnings,
        )

        self._apply_predictability_checks(
            password=normalized_password,
            user=user,
            email=email,
            banned_fragments=banned_fragments or [],
            errors=errors,
            warnings=warnings,
        )

        strength = self.calculate_strength(normalized_password)

        suggestions = self.get_suggestions(
            password=normalized_password,
            errors=errors,
            warnings=warnings,
        )

        deduped_errors = self._dedupe(errors)
        deduped_warnings = self._dedupe(warnings)

        return {
            "valid": len(deduped_errors) == 0,
            "errors": deduped_errors,
            "warnings": deduped_warnings,
            "strength": strength,
            "strength_label": self.get_strength_label(strength),
            "suggestions": suggestions,
            "meets_requirements": len(deduped_errors) == 0,
        }

    def enforce(
        self,
        password: str,
        user=None,
        context: str = Context.REGISTRATION,
        email: str | None = None,
        banned_fragments: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Validate password and raise if requirements are not met.

        Args:
            password: Password to validate.
            user: Optional user object.
            context: Validation context.
            email: Optional email address.
            banned_fragments: Optional forbidden substrings.

        Returns:
            Validation result dictionary.

        Raises:
            ValueError: If password validation fails.
        """
        result = self.validate_password(
            password=password,
            user=user,
            context=context,
            email=email,
            banned_fragments=banned_fragments,
        )

        if not result["valid"]:
            raise ValueError(result["errors"])

        return result

    def calculate_strength(self, password: str) -> int:
        """
        Calculate password strength score from 0 to 100.

        Args:
            password: Password to score.

        Returns:
            Integer strength score.
        """
        score = 0

        length = len(password)

        if length >= 8:
            score += 20
        if length >= 12:
            score += 15
        if length >= 16:
            score += 10

        if re.search(r"[a-z]", password):
            score += 10
        if re.search(r"[A-Z]", password):
            score += 10
        if re.search(r"\d", password):
            score += 10
        if re.search(self.SPECIAL_CHAR_PATTERN, password):
            score += 10

        if not self.is_common_password(password):
            score += 10
        if not self.has_sequential_chars(password):
            score += 5
        if not self.has_repeated_chars(password):
            score += 5
        if " " not in password and length >= 14:
            score += 5

        return min(score, 100)

    def get_strength_label(self, strength: int) -> str:
        """
        Convert numeric strength to label.

        Args:
            strength: Strength score.

        Returns:
            Human-readable strength label.
        """
        if strength < 30:
            return "Very Weak"
        if strength < 50:
            return "Weak"
        if strength < 70:
            return "Fair"
        if strength < 90:
            return "Good"
        return "Strong"

    def is_common_password(self, password: str) -> bool:
        """
        Check if password is in common-password list.

        Args:
            password: Password to test.

        Returns:
            True if common, otherwise False.
        """
        return password.lower() in self.COMMON_PASSWORDS

    def has_sequential_chars(self, password: str) -> bool:
        """
        Check for ascending or descending character sequences.

        Examples:
            1234, 4321, abcd, dcba

        Args:
            password: Password to inspect.

        Returns:
            True if a sequential pattern exists, otherwise False.
        """
        password_lower = password.lower()

        for i in range(len(password_lower) - 3):
            chunk = password_lower[i:i + 4]

            if chunk.isdigit():
                digits = [int(c) for c in chunk]
                if self._is_step_sequence(digits):
                    return True

            if chunk.isalpha():
                codes = [ord(c) for c in chunk]
                if self._is_step_sequence(codes):
                    return True

        return False

    def has_repeated_chars(self, password: str) -> bool:
        """
        Check for repeated characters appearing too many times.

        Args:
            password: Password to inspect.

        Returns:
            True if repeated-character pattern exists.
        """
        return bool(re.search(r"(.)\1{2,}", password))

    def get_suggestions(
        self,
        password: str,
        errors: list[str],
        warnings: list[str],
    ) -> list[str]:
        """
        Generate improvement suggestions.

        Args:
            password: Password being evaluated.
            errors: Validation errors.
            warnings: Validation warnings.

        Returns:
            List of improvement suggestions.
        """
        suggestions: list[str] = []

        if len(password) < 12:
            suggestions.append("Use at least 12 characters.")

        if not re.search(r"[A-Z]", password):
            suggestions.append("Add uppercase letters.")

        if not re.search(r"[a-z]", password):
            suggestions.append("Add lowercase letters.")

        if not re.search(r"\d", password):
            suggestions.append("Add numbers.")

        if not re.search(self.SPECIAL_CHAR_PATTERN, password):
            suggestions.append("Add special characters.")

        if self.is_common_password(password):
            suggestions.append("Avoid common words and passwords.")

        if self.has_sequential_chars(password):
            suggestions.append("Avoid sequences like 1234 or abcd.")

        if self.has_repeated_chars(password):
            suggestions.append("Avoid repeated characters.")

        return self._dedupe(suggestions)[:5]

    def _apply_base_rules(
        self,
        *,
        password: str,
        errors: list[str],
    ) -> None:
        """
        Apply rules that always matter.

        Args:
            password: Password to validate.
            errors: Mutable list of errors.
        """
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")

        if self.is_common_password(password):
            errors.append(
                "This password is too common. Please choose a "
                "stronger, unique password."
            )

    def _apply_context_rules(
        self,
        *,
        password: str,
        context: str,
        errors: list[str],
        warnings: list[str],
    ) -> None:
        """
        Apply context-sensitive password rules.

        Args:
            password: Password to validate.
            context: Validation context.
            errors: Mutable list of errors.
            warnings: Mutable list of warnings.
        """
        if context in {
            self.Context.PASSWORD_CHANGE,
            self.Context.PASSWORD_RESET,
            self.Context.ADMIN_ACTION,
        }:
            if not re.search(r"[A-Z]", password):
                errors.append(
                    "Password must contain at least one uppercase letter."
                )
            if not re.search(r"[a-z]", password):
                errors.append(
                    "Password must contain at least one lowercase letter."
                )
            if not re.search(r"\d", password):
                errors.append(
                    "Password must contain at least one number."
                )
            if not re.search(self.SPECIAL_CHAR_PATTERN, password):
                warnings.append(
                    "Consider adding a special character for "
                    "stronger security."
                )

        elif context == self.Context.REGISTRATION:
            if len(password) < 12:
                warnings.append(
                    "Consider using at least 12 characters."
                )
            if not any(c.isupper() for c in password):
                warnings.append(
                    "Consider mixing uppercase and lowercase letters."
                )

    def _apply_predictability_checks(
        self,
        *,
        password: str,
        user,
        email: str | None,
        banned_fragments: list[str],
        errors: list[str],
        warnings: list[str],
    ) -> None:
        """
        Apply predictability and identity-based checks.

        Args:
            password: Password to validate.
            user: Optional user object.
            email: Optional email address.
            banned_fragments: Additional forbidden fragments.
            errors: Mutable list of errors.
            warnings: Mutable list of warnings.
        """
        lowered_password = password.lower()

        fragments: list[str] = []

        if email:
            email_name = email.split("@")[0].strip().lower()
            if email_name:
                fragments.append(email_name)

        if user is not None:
            username = getattr(user, "username", None)
            first_name = getattr(user, "first_name", None)
            last_name = getattr(user, "last_name", None)

            for value in [username, first_name, last_name]:
                if value:
                    fragments.append(str(value).strip().lower())

        for fragment in banned_fragments:
            if fragment:
                fragments.append(str(fragment).strip().lower())

        for fragment in fragments:
            if len(fragment) >= 3 and fragment in lowered_password:
                warnings.append(
                    f"Avoid using personal or predictable text like "
                    f"'{fragment}' in your password."
                )

        if self.has_repeated_chars(password):
            warnings.append(
                "Avoid using the same character repeatedly."
            )

        if self.has_sequential_chars(password):
            warnings.append(
                "Avoid sequential characters like 1234 or abcd."
            )

    @staticmethod
    def _is_step_sequence(values: list[int]) -> bool:
        """
        Check whether values form an ascending or descending sequence.

        Args:
            values: List of numeric values.

        Returns:
            True if values step consistently by +1 or -1.
        """
        if len(values) < 2:
            return False

        diffs = [values[i + 1] - values[i] for i in range(len(values) - 1)]
        return all(diff == 1 for diff in diffs) or all(
            diff == -1 for diff in diffs
        )

    @staticmethod
    def _dedupe(items: list[str]) -> list[str]:
        """
        Remove duplicates while preserving order.

        Args:
            items: List of strings.

        Returns:
            Deduplicated list.
        """
        seen = set()
        deduped = []

        for item in items:
            if item not in seen:
                seen.add(item)
                deduped.append(item)

        return deduped