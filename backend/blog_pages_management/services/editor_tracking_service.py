"""
Service for tracking editor usage and productivity.
"""
from typing import Optional, Dict
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import timedelta

from ..models.editor_usage_tracking import EditorSession, EditorAction, EditorProductivityMetrics


class EditorTrackingService:
    """
    Service for tracking and analyzing editor usage.
    """
    
    @staticmethod
    def start_session(user, website, content_object) -> EditorSession:
        """
        Start a new editor session.
        
        Args:
            user: User editing
            website: Website being edited for
            content_object: The content being edited (BlogPost, ServicePage, etc.)
        
        Returns:
            EditorSession instance
        """
        # End any active sessions for this user/content
        active_sessions = EditorSession.objects.filter(
            user=user,
            content_type=ContentType.objects.get_for_model(content_object),
            content_id=content_object.id,
            is_active=True
        )
        for session in active_sessions:
            session.end_session()
        
        # Create new session
        session = EditorSession.objects.create(
            user=user,
            website=website,
            content_type=ContentType.objects.get_for_model(content_object),
            content_id=content_object.id,
            is_active=True
        )
        
        return session
    
    @staticmethod
    def end_session(session_id: int) -> Optional[EditorSession]:
        """End an editor session."""
        try:
            session = EditorSession.objects.get(id=session_id, is_active=True)
            session.end_session()
            return session
        except EditorSession.DoesNotExist:
            return None
    
    @staticmethod
    def track_action(
        session_id: int,
        action_type: str,
        metadata: Optional[Dict] = None
    ) -> Optional[EditorAction]:
        """
        Track an editor action.
        
        Args:
            session_id: Editor session ID
            action_type: Type of action (from EditorAction.ACTION_TYPES)
            metadata: Optional metadata about the action
        
        Returns:
            EditorAction instance
        """
        try:
            session = EditorSession.objects.get(id=session_id, is_active=True)
            
            action = EditorAction.objects.create(
                session=session,
                action_type=action_type,
                metadata=metadata or {}
            )
            
            # Update session metrics
            session.total_actions += 1
            
            # Update specific counters
            if action_type == 'template_use':
                session.templates_used += 1
            elif action_type == 'snippet_use':
                session.snippets_used += 1
            elif action_type == 'block_use':
                session.blocks_used += 1
            elif action_type == 'health_check':
                session.health_checks_run += 1
            elif action_type == 'auto_save':
                session.auto_saves_count += 1
            elif action_type == 'save':
                session.manual_saves_count += 1
            elif action_type == 'keystroke':
                session.total_keystrokes += 1
                if metadata:
                    session.characters_added += metadata.get('characters_added', 0)
                    session.characters_removed += metadata.get('characters_removed', 0)
            
            session.save()
            
            return action
        except EditorSession.DoesNotExist:
            return None
    
    @staticmethod
    def calculate_productivity_metrics(
        user,
        website,
        period_start=None,
        period_end=None
    ) -> EditorProductivityMetrics:
        """
        Calculate productivity metrics for a user/website over a period.
        
        Args:
            user: User to calculate for
            website: Website to calculate for
            period_start: Start date (defaults to 30 days ago)
            period_end: End date (defaults to today)
        
        Returns:
            EditorProductivityMetrics instance
        """
        if not period_end:
            period_end = timezone.now().date()
        if not period_start:
            period_start = period_end - timedelta(days=30)
        
        # Get or create metrics
        metrics, created = EditorProductivityMetrics.objects.get_or_create(
            user=user,
            website=website,
            period_start=period_start,
            period_end=period_end,
            defaults={}
        )
        
        # Get sessions in period
        sessions = EditorSession.objects.filter(
            user=user,
            website=website,
            session_start__date__gte=period_start,
            session_start__date__lte=period_end
        )
        
        if not sessions.exists():
            return metrics
        
        # Calculate metrics
        metrics.total_sessions = sessions.count()
        
        # Session durations
        durations = []
        longest = 0
        for session in sessions:
            if session.session_end:
                duration = (session.session_end - session.session_start).total_seconds() / 60
            else:
                duration = (timezone.now() - session.session_start).total_seconds() / 60
            durations.append(duration)
            longest = max(longest, duration)
        
        metrics.average_session_duration = sum(durations) / len(durations) if durations else 0
        metrics.longest_session = longest
        
        # Activity metrics
        total_keystrokes = sum(s.total_keystrokes for s in sessions)
        metrics.total_keystrokes = total_keystrokes
        metrics.average_keystrokes_per_session = total_keystrokes / metrics.total_sessions if metrics.total_sessions > 0 else 0
        
        total_chars = sum(s.characters_added for s in sessions)
        metrics.total_characters_written = total_chars
        
        # Tool usage
        metrics.templates_used_count = sum(s.templates_used for s in sessions)
        metrics.snippets_used_count = sum(s.snippets_used for s in sessions)
        metrics.blocks_used_count = sum(s.blocks_used for s in sessions)
        metrics.health_checks_count = sum(s.health_checks_run for s in sessions)
        
        # Words per minute (estimate: 5 chars per word)
        total_minutes = sum(durations)
        if total_minutes > 0:
            words = total_chars / 5
            metrics.words_per_minute = words / total_minutes
        else:
            metrics.words_per_minute = 0
        
        # Calculate productivity score (0-100)
        # Factors: session frequency, tool usage, content quality, efficiency
        score = 0
        
        # Session frequency (0-25 points)
        if metrics.total_sessions >= 20:
            score += 25
        elif metrics.total_sessions >= 10:
            score += 15
        elif metrics.total_sessions >= 5:
            score += 10
        
        # Tool usage (0-25 points)
        tool_score = min(25, (metrics.templates_used_count + metrics.snippets_used_count + metrics.blocks_used_count) / 2)
        score += tool_score
        
        # Efficiency (0-25 points) - based on words per minute
        if metrics.words_per_minute >= 40:
            score += 25
        elif metrics.words_per_minute >= 30:
            score += 20
        elif metrics.words_per_minute >= 20:
            score += 15
        elif metrics.words_per_minute >= 10:
            score += 10
        
        # Activity level (0-25 points) - based on keystrokes
        if metrics.total_keystrokes >= 10000:
            score += 25
        elif metrics.total_keystrokes >= 5000:
            score += 20
        elif metrics.total_keystrokes >= 2000:
            score += 15
        elif metrics.total_keystrokes >= 1000:
            score += 10
        
        metrics.productivity_score = min(100, score)
        metrics.save()
        
        return metrics

