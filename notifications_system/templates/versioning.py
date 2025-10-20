"""
Template versioning and A/B testing system.
"""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from django.core.cache import cache
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)


class TemplateVersion(models.Model):
    """Template version for A/B testing and versioning."""
    
    event_key = models.CharField(max_length=100, db_index=True)
    version = models.CharField(max_length=20, default="v1.0")
    template_type = models.CharField(max_length=20, choices=[
        ('class_based', 'Class Based'),
        ('database', 'Database'),
        ('generic', 'Generic'),
        ('emergency', 'Emergency')
    ])
    content_hash = models.CharField(max_length=64, db_index=True)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # A/B Testing fields
    traffic_percentage = models.FloatField(default=100.0)  # 0-100
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Performance metrics
    render_count = models.PositiveIntegerField(default=0)
    success_count = models.PositiveIntegerField(default=0)
    error_count = models.PositiveIntegerField(default=0)
    avg_render_time = models.FloatField(default=0.0)
    
    class Meta:
        unique_together = ['event_key', 'version']
        indexes = [
            models.Index(fields=['event_key', 'is_active']),
            models.Index(fields=['event_key', 'version']),
        ]
    
    def __str__(self):
        return f"{self.event_key} v{self.version}"
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.render_count == 0:
            return 0.0
        return (self.success_count / self.render_count) * 100
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate percentage."""
        if self.render_count == 0:
            return 0.0
        return (self.error_count / self.render_count) * 100
    
    def is_eligible_for_user(self, user_id: int) -> bool:
        """Check if this version is eligible for a specific user."""
        if not self.is_active:
            return False
        
        # Check date range
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        
        # Check traffic percentage using consistent hashing
        if self.traffic_percentage < 100.0:
            user_hash = hashlib.md5(f"{user_id}_{self.event_key}".encode()).hexdigest()
            user_percentage = int(user_hash[:8], 16) / 0xffffffff * 100
            return user_percentage <= self.traffic_percentage
        
        return True


class ABTest(models.Model):
    """A/B test configuration for templates."""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    event_key = models.CharField(max_length=100)
    
    # Test configuration
    is_active = models.BooleanField(default=False)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    traffic_percentage = models.FloatField(default=10.0)  # 0-100
    
    # Test variants
    control_version = models.ForeignKey(
        TemplateVersion, 
        on_delete=models.CASCADE, 
        related_name='control_tests'
    )
    test_version = models.ForeignKey(
        TemplateVersion, 
        on_delete=models.CASCADE, 
        related_name='test_tests'
    )
    
    # Success criteria
    primary_metric = models.CharField(max_length=50, default='success_rate')
    target_improvement = models.FloatField(default=5.0)  # 5% improvement
    minimum_sample_size = models.PositiveIntegerField(default=1000)
    
    # Results
    control_metrics = models.JSONField(default=dict)
    test_metrics = models.JSONField(default=dict)
    is_significant = models.BooleanField(default=False)
    confidence_level = models.FloatField(default=0.95)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"A/B Test: {self.name}"
    
    @property
    def is_running(self) -> bool:
        """Check if the A/B test is currently running."""
        now = timezone.now()
        return (
            self.is_active and 
            self.start_date <= now <= self.end_date
        )
    
    @property
    def sample_size(self) -> int:
        """Get current sample size."""
        return (
            self.control_version.render_count + 
            self.test_version.render_count
        )
    
    def calculate_results(self):
        """Calculate A/B test results."""
        if not self.is_running:
            return
        
        # Calculate metrics for both variants
        self.control_metrics = {
            'render_count': self.control_version.render_count,
            'success_count': self.control_version.success_count,
            'error_count': self.control_version.error_count,
            'success_rate': self.control_version.success_rate,
            'avg_render_time': self.control_version.avg_render_time,
        }
        
        self.test_metrics = {
            'render_count': self.test_version.render_count,
            'success_count': self.test_version.success_count,
            'error_count': self.test_version.error_count,
            'success_rate': self.test_version.success_rate,
            'avg_render_time': self.test_version.avg_render_time,
        }
        
        # Calculate statistical significance
        self.is_significant = self._calculate_significance()
        self.save()
    
    def _calculate_significance(self) -> bool:
        """Calculate if the test results are statistically significant."""
        # Simplified significance test
        control_rate = self.control_metrics.get('success_rate', 0)
        test_rate = self.test_metrics.get('success_rate', 0)
        
        if control_rate == 0 or test_rate == 0:
            return False
        
        # Basic z-test for proportions
        improvement = test_rate - control_rate
        return improvement >= self.target_improvement


class TemplateVersionManager:
    """Manager for template versioning and A/B testing."""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
    
    def get_version_for_user(
        self, 
        event_key: str, 
        user_id: int,
        template_type: str = "class_based"
    ) -> Optional[TemplateVersion]:
        """Get the appropriate template version for a user."""
        cache_key = f"template_version:{event_key}:{user_id}:{template_type}"
        cached_version = cache.get(cache_key)
        
        if cached_version:
            return cached_version
        
        # Check for active A/B tests
        ab_test = self._get_active_ab_test(event_key, user_id)
        if ab_test:
            version = self._select_ab_test_version(ab_test, user_id)
        else:
            version = self._get_default_version(event_key, template_type)
        
        if version:
            cache.set(cache_key, version, self.cache_timeout)
        
        return version
    
    def _get_active_ab_test(self, event_key: str, user_id: int) -> Optional[ABTest]:
        """Get active A/B test for event and user."""
        now = timezone.now()
        
        ab_tests = ABTest.objects.filter(
            event_key=event_key,
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).select_related('control_version', 'test_version')
        
        for ab_test in ab_tests:
            if ab_test.is_eligible_for_user(user_id):
                return ab_test
        
        return None
    
    def _select_ab_test_version(self, ab_test: ABTest, user_id: int) -> TemplateVersion:
        """Select version for A/B test."""
        # Use consistent hashing to assign users to variants
        user_hash = hashlib.md5(f"{user_id}_{ab_test.id}".encode()).hexdigest()
        user_percentage = int(user_hash[:8], 16) / 0xffffffff * 100
        
        if user_percentage <= 50:  # 50/50 split
            return ab_test.control_version
        else:
            return ab_test.test_version
    
    def _get_default_version(self, event_key: str, template_type: str) -> Optional[TemplateVersion]:
        """Get default version for event."""
        return TemplateVersion.objects.filter(
            event_key=event_key,
            template_type=template_type,
            is_active=True,
            is_default=True
        ).first()
    
    def record_render(
        self, 
        version: TemplateVersion, 
        success: bool, 
        render_time: float
    ):
        """Record template render metrics."""
        version.render_count += 1
        
        if success:
            version.success_count += 1
        else:
            version.error_count += 1
        
        # Update average render time
        total_time = version.avg_render_time * (version.render_count - 1) + render_time
        version.avg_render_time = total_time / version.render_count
        
        version.save(update_fields=[
            'render_count', 'success_count', 'error_count', 'avg_render_time'
        ])
        
        # Update A/B test results if applicable
        self._update_ab_test_results(version)
    
    def _update_ab_test_results(self, version: TemplateVersion):
        """Update A/B test results when metrics change."""
        ab_tests = ABTest.objects.filter(
            models.Q(control_version=version) | models.Q(test_version=version),
            is_active=True
        )
        
        for ab_test in ab_tests:
            ab_test.calculate_results()
    
    def create_version(
        self,
        event_key: str,
        version: str,
        template_type: str,
        content_hash: str,
        is_default: bool = False,
        traffic_percentage: float = 100.0
    ) -> TemplateVersion:
        """Create a new template version."""
        # Deactivate other default versions if this is the new default
        if is_default:
            TemplateVersion.objects.filter(
                event_key=event_key,
                template_type=template_type,
                is_default=True
            ).update(is_default=False)
        
        return TemplateVersion.objects.create(
            event_key=event_key,
            version=version,
            template_type=template_type,
            content_hash=content_hash,
            is_default=is_default,
            traffic_percentage=traffic_percentage
        )
    
    def create_ab_test(
        self,
        name: str,
        event_key: str,
        control_version: TemplateVersion,
        test_version: TemplateVersion,
        start_date: datetime,
        end_date: datetime,
        traffic_percentage: float = 10.0
    ) -> ABTest:
        """Create a new A/B test."""
        return ABTest.objects.create(
            name=name,
            event_key=event_key,
            control_version=control_version,
            test_version=test_version,
            start_date=start_date,
            end_date=end_date,
            traffic_percentage=traffic_percentage
        )


# Global version manager
_version_manager = TemplateVersionManager()

def get_version_manager() -> TemplateVersionManager:
    """Get the global template version manager."""
    return _version_manager


def get_template_version(
    event_key: str, 
    user_id: int, 
    template_type: str = "class_based"
) -> Optional[TemplateVersion]:
    """Get template version for user."""
    manager = get_version_manager()
    return manager.get_version_for_user(event_key, user_id, template_type)


def record_template_render(
    version: TemplateVersion, 
    success: bool, 
    render_time: float
):
    """Record template render metrics."""
    manager = get_version_manager()
    manager.record_render(version, success, render_time)
