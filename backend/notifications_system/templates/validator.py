"""
Template validation and testing framework.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple, Type
from notifications_system.templates.base import BaseNotificationTemplate
from notifications_system.registry.template_registry import get_template, _TEMPLATE_CLASSES

logger = logging.getLogger(__name__)


class TemplateValidator:
    """Validates notification templates for correctness and completeness."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_all_templates(self) -> Tuple[bool, List[str], List[str]]:
        """
        Validate all registered templates.
        
        Returns:
            (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        for event_key, template_class in _TEMPLATE_CLASSES.items():
            self._validate_template_class(event_key, template_class)
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _validate_template_class(self, event_key: str, template_class: Type[BaseNotificationTemplate]):
        """Validate a single template class."""
        try:
            # Test template instantiation
            template = template_class()
            
            # Validate metadata
            self._validate_template_metadata(event_key, template)
            
            # Test rendering with sample data
            self._test_template_rendering(event_key, template)
            
        except Exception as e:
            self.errors.append(f"Template {event_key}: Failed to instantiate - {e}")
    
    def _validate_template_metadata(self, event_key: str, template: BaseNotificationTemplate):
        """Validate template metadata."""
        # Check event_name matches registration
        if template.event_name != event_key:
            self.errors.append(
                f"Template {event_key}: event_name mismatch - "
                f"expected '{event_key}', got '{template.event_name}'"
            )
        
        # Check required context is defined
        if not hasattr(template, 'requires_context'):
            self.warnings.append(f"Template {event_key}: Missing requires_context attribute")
        elif not isinstance(template.requires_context, list):
            self.warnings.append(f"Template {event_key}: requires_context should be a list")
        
        # Check channels are valid
        if hasattr(template, 'channels'):
            valid_channels = ["email", "in_app", "sms", "push", "webhook", "telegram", "whatsapp", "sse", "ws", "slack", "discord"]
            for channel in template.channels:
                if channel not in valid_channels:
                    self.warnings.append(
                        f"Template {event_key}: Invalid channel '{channel}' - "
                        f"valid channels: {', '.join(valid_channels)}"
                    )
    
    def _test_template_rendering(self, event_key: str, template: BaseNotificationTemplate):
        """Test template rendering with sample data."""
        try:
            # Generate sample context based on template requirements
            sample_context = self._generate_sample_context(template)
            
            # Test rendering
            title, text, html = template.render(sample_context)
            
            # Validate output
            self._validate_rendered_output(event_key, title, text, html)
            
        except Exception as e:
            self.errors.append(f"Template {event_key}: Rendering failed - {e}")
    
    def _generate_sample_context(self, template: BaseNotificationTemplate) -> Dict[str, Any]:
        """Generate sample context for testing."""
        context = {}
        
        # Add required context fields
        for field in getattr(template, 'requires_context', []):
            if field == "user":
                context[field] = {
                    "id": 1,
                    "username": "testuser",
                    "first_name": "Test",
                    "last_name": "User",
                    "email": "test@example.com"
                }
            elif field == "order":
                context[field] = {
                    "id": 123,
                    "title": "Test Order",
                    "status": "pending",
                    "amount": 100.00,
                    "currency": "USD"
                }
            elif field == "wallet":
                context[field] = {
                    "balance": 500.00,
                    "currency": "USD"
                }
            elif field == "website":
                context[field] = {
                    "id": 1,
                    "name": "Test Website",
                    "domain": "test.example.com"
                }
            else:
                context[field] = f"sample_{field}"
        
        # Add optional context fields
        for field in getattr(template, 'optional_context', []):
            if field == "frontend_url":
                context[field] = "https://example.com"
            elif field == "actor":
                context[field] = {
                    "id": 2,
                    "username": "admin",
                    "first_name": "Admin",
                    "last_name": "User"
                }
            else:
                context[field] = f"sample_{field}"
        
        return context
    
    def _validate_rendered_output(self, event_key: str, title: str, text: str, html: str):
        """Validate rendered template output."""
        # Check all outputs are strings
        if not isinstance(title, str):
            self.errors.append(f"Template {event_key}: Title must be a string")
        if not isinstance(text, str):
            self.errors.append(f"Template {event_key}: Text must be a string")
        if not isinstance(html, str):
            self.errors.append(f"Template {event_key}: HTML must be a string")
        
        # Check outputs are not empty
        if not title.strip():
            self.warnings.append(f"Template {event_key}: Title is empty")
        if not text.strip():
            self.warnings.append(f"Template {event_key}: Text is empty")
        if not html.strip():
            self.warnings.append(f"Template {event_key}: HTML is empty")
        
        # Check for potential security issues
        if "<script" in html.lower():
            self.warnings.append(f"Template {event_key}: HTML contains script tags - potential security risk")
        
        # Check for basic HTML structure
        if html and not ("<" in html and ">" in html):
            self.warnings.append(f"Template {event_key}: HTML appears to be plain text")


class TemplateTester:
    """Test notification templates with various scenarios."""
    
    def __init__(self):
        self.test_results: Dict[str, List[Dict[str, Any]]] = {}
    
    def run_all_tests(self) -> Dict[str, List[Dict[str, Any]]]:
        """Run all template tests."""
        self.test_results = {}
        
        for event_key, template_class in _TEMPLATE_CLASSES.items():
            self.test_results[event_key] = self._test_template(event_key, template_class)
        
        return self.test_results
    
    def _test_template(self, event_key: str, template_class: Type[BaseNotificationTemplate]) -> List[Dict[str, Any]]:
        """Test a single template with various scenarios."""
        results = []
        
        # Test 1: Basic rendering
        try:
            template = template_class()
            sample_context = self._generate_sample_context(template)
            title, text, html = template.render(sample_context)
            
            results.append({
                "test": "basic_rendering",
                "status": "passed",
                "title": title,
                "text": text[:100] + "..." if len(text) > 100 else text,
                "html": html[:100] + "..." if len(html) > 100 else html,
            })
        except Exception as e:
            results.append({
                "test": "basic_rendering",
                "status": "failed",
                "error": str(e)
            })
        
        # Test 2: Missing required context
        try:
            template = template_class()
            # Try rendering with minimal context
            title, text, html = template.render({})
            results.append({
                "test": "missing_context",
                "status": "passed" if not title.strip() else "warning",
                "message": "Template handled missing context gracefully"
            })
        except Exception as e:
            results.append({
                "test": "missing_context",
                "status": "failed",
                "error": str(e)
            })
        
        # Test 3: Performance test
        try:
            template = template_class()
            sample_context = self._generate_sample_context(template)
            
            import time
            start_time = time.time()
            for _ in range(100):  # Render 100 times
                template.render(sample_context)
            end_time = time.time()
            
            avg_time = (end_time - start_time) / 100
            results.append({
                "test": "performance",
                "status": "passed" if avg_time < 0.01 else "warning",
                "avg_render_time": f"{avg_time:.4f}s",
                "message": "Performance test completed"
            })
        except Exception as e:
            results.append({
                "test": "performance",
                "status": "failed",
                "error": str(e)
            })
        
        return results
    
    def _generate_sample_context(self, template: BaseNotificationTemplate) -> Dict[str, Any]:
        """Generate sample context for testing."""
        context = {}
        
        # Add required context fields
        for field in getattr(template, 'requires_context', []):
            if field == "user":
                context[field] = {
                    "id": 1,
                    "username": "testuser",
                    "first_name": "Test",
                    "last_name": "User",
                    "email": "test@example.com"
                }
            elif field == "order":
                context[field] = {
                    "id": 123,
                    "title": "Test Order",
                    "status": "pending",
                    "amount": 100.00,
                    "currency": "USD"
                }
            elif field == "wallet":
                context[field] = {
                    "balance": 500.00,
                    "currency": "USD"
                }
            elif field == "website":
                context[field] = {
                    "id": 1,
                    "name": "Test Website",
                    "domain": "test.example.com"
                }
            else:
                context[field] = f"sample_{field}"
        
        # Add optional context fields
        for field in getattr(template, 'optional_context', []):
            if field == "frontend_url":
                context[field] = "https://example.com"
            elif field == "actor":
                context[field] = {
                    "id": 2,
                    "username": "admin",
                    "first_name": "Admin",
                    "last_name": "User"
                }
            else:
                context[field] = f"sample_{field}"
        
        return context


def validate_all_templates() -> Tuple[bool, List[str], List[str]]:
    """Convenience function to validate all templates."""
    validator = TemplateValidator()
    return validator.validate_all_templates()


def test_all_templates() -> Dict[str, List[Dict[str, Any]]]:
    """Convenience function to test all templates."""
    tester = TemplateTester()
    return tester.run_all_tests()
