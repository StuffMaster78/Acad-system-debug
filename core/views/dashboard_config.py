"""
Dashboard Configuration API Views
Serves dashboard card configurations and font settings based on user role
"""

from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.models.dashboard_config import DashboardCardConfig, DashboardFontConfig
from websites.utils import get_current_website


class DashboardConfigView(APIView):
    """
    Get dashboard configuration (cards, fonts, colors) for the current user's role
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        user_role = getattr(user, 'role', 'client')
        website = getattr(user, 'website', None) or get_current_website(request)
        
        # Get font configuration
        font_config = None
        try:
            if website:
                font_config = DashboardFontConfig.objects.filter(website=website).first()
            if not font_config:
                font_config = DashboardFontConfig.objects.filter(website__isnull=True).first()
        except Exception:
            pass
        
        # Get card configurations for this role
        cards = DashboardCardConfig.objects.filter(
            is_active=True,
            allowed_roles__contains=[user_role]
        )
        
        # Filter by website if specified
        if website:
            cards = cards.filter(
                models.Q(website=website) | models.Q(website__isnull=True)
            )
        else:
            cards = cards.filter(website__isnull=True)
        
        # Order by position
        cards = cards.order_by('position', 'title')
        
        # Serialize cards
        cards_data = []
        for card in cards:
            cards_data.append({
                'key': card.card_key,
                'title': card.title,
                'description': card.description,
                'icon': card.icon,
                'color': card.color,
                'data_source': card.data_source,
                'data_type': card.data_type,
                'badge_text': card.badge_text,
                'position': card.position,
                'config': card.config,
            })
        
        # Serialize font config
        font_data = None
        if font_config:
            font_data = {
                'font_family': font_config.font_family,
                'font_url': font_config.font_url,
                'base_font_size': font_config.base_font_size,
                'card_value_font_size': font_config.card_value_font_size,
                'card_label_font_size': font_config.card_label_font_size,
            }
        else:
            # Default font config
            font_data = {
                'font_family': "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                'font_url': '',
                'base_font_size': '16px',
                'card_value_font_size': 'clamp(24px, 3vw, 32px)',
                'card_label_font_size': '13px',
            }
        
        return Response({
            'role': user_role,
            'cards': cards_data,
            'font_config': font_data,
        }, status=status.HTTP_200_OK)

