"""
Unified API endpoint for all dropdown/select list options.
All dropdowns should draw from the database or exposed enums.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from websites.models import Website
from order_configs.models import (
    PaperType, FormattingandCitationStyle, Subject,
    AcademicLevel, TypeOfWork, EnglishType
)
from orders.order_enums import OrderStatus, OrderPaymentStatus, DisputeStatusEnum, SpacingOptions
from order_payments_management.models import STATUS_CHOICES, PAYMENT_TYPE_CHOICES
from fines.models import FineType, FineStatus
from class_management.models import ClassDurationOption
from users.models import User


class DropdownOptionsView(APIView):
    """
    Unified endpoint for all dropdown/select list options.
    Returns database-driven options and enum choices.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get all dropdown options.
        
        Query params:
        - website_id: Filter order configs by website
        - include_enums: Include enum choices (default: true)
        - include_configs: Include order configs (default: true)
        - include_websites: Include websites list (default: true)
        - include_users: Include users list (default: false, admin only)
        """
        website_id = request.query_params.get('website_id')
        include_enums = request.query_params.get('include_enums', 'true').lower() == 'true'
        include_configs = request.query_params.get('include_configs', 'true').lower() == 'true'
        include_websites = request.query_params.get('include_websites', 'true').lower() == 'true'
        include_users = request.query_params.get('include_users', 'false').lower() == 'true'
        
        # Get user's website if not superadmin
        user_website = None
        if request.user.role != 'superadmin':
            user_website = getattr(request.user, 'website', None)
            if user_website:
                website_id = str(user_website.id)
        
        response_data = {}
        
        # Order Configurations (Database-driven)
        if include_configs:
            website_filter = Q()
            if website_id:
                website_filter = Q(website_id=website_id)
            elif user_website:
                website_filter = Q(website=user_website)
            
            response_data['order_configs'] = {
                'paper_types': [
                    {'id': pt.id, 'name': pt.name, 'website_id': pt.website_id}
                    for pt in PaperType.objects.filter(website_filter).select_related('website').order_by('name')
                ],
                'formatting_styles': [
                    {'id': fs.id, 'name': fs.name, 'website_id': fs.website_id}
                    for fs in FormattingandCitationStyle.objects.filter(website_filter).select_related('website').order_by('name')
                ],
                'subjects': [
                    {'id': s.id, 'name': s.name, 'is_technical': s.is_technical, 'website_id': s.website_id}
                    for s in Subject.objects.filter(website_filter).select_related('website').order_by('name')
                ],
                'academic_levels': [
                    {'id': al.id, 'name': al.name, 'website_id': al.website_id}
                    for al in AcademicLevel.objects.filter(website_filter).select_related('website').order_by('name')
                ],
                'types_of_work': [
                    {'id': tow.id, 'name': tow.name, 'website_id': tow.website_id}
                    for tow in TypeOfWork.objects.filter(website_filter).select_related('website').order_by('name')
                ],
                'english_types': [
                    {'id': et.id, 'name': et.name, 'code': et.code, 'website_id': et.website_id}
                    for et in EnglishType.objects.filter(website_filter).select_related('website').order_by('name')
                ],
            }
        
        # Enum Choices (Status, Payment Types, etc.)
        if include_enums:
            response_data['enums'] = {
                'order_status': [
                    {'value': status.value, 'label': status.name.replace('_', ' ').title()}
                    for status in OrderStatus
                ],
                'payment_status': [
                    {'value': status.value, 'label': status.name.replace('_', ' ').title()}
                    for status in OrderPaymentStatus
                ],
                'payment_status_choices': [
                    {'value': choice[0], 'label': choice[1]}
                    for choice in STATUS_CHOICES
                ],
                'payment_types': [
                    {'value': choice[0], 'label': choice[1]}
                    for choice in PAYMENT_TYPE_CHOICES
                ],
                'spacing_options': [
                    {'value': option.value, 'label': option.name.replace('_', ' ').title()}
                    for option in SpacingOptions
                ],
                'dispute_status': [
                    {'value': status.value, 'label': status.name.replace('_', ' ').title()}
                    for status in DisputeStatusEnum
                ],
                'fine_types': [
                    {'value': choice.value, 'label': choice.label}
                    for choice in FineType
                ],
                'fine_status': [
                    {'value': choice.value, 'label': choice.label}
                    for choice in FineStatus
                ],
            }
        
        # Websites List
        if include_websites:
            websites_qs = Website.objects.filter(is_active=True, is_deleted=False)
            if request.user.role != 'superadmin' and user_website:
                websites_qs = websites_qs.filter(id=user_website.id)
            
            response_data['websites'] = [
                {'id': w.id, 'name': w.name, 'domain': w.domain}
                for w in websites_qs.order_by('name')
            ]
        
        # Class Duration Options (Database-driven)
        if include_configs:
            duration_filter = Q()
            if website_id:
                duration_filter = Q(website_id=website_id)
            elif user_website:
                duration_filter = Q(website=user_website)
            
            response_data['class_duration_options'] = [
                {'id': opt.id, 'class_code': opt.class_code, 'label': opt.label, 'website_id': opt.website_id}
                for opt in ClassDurationOption.objects.filter(duration_filter, is_active=True)
                .select_related('website')
                .order_by('website', 'class_code')
            ]
        
        # Users List (Admin only, optional)
        if include_users and request.user.role in ['superadmin', 'admin']:
            users_qs = User.objects.filter(is_active=True)
            if request.user.role == 'admin' and user_website:
                # Admins see users from their website
                users_qs = users_qs.filter(website=user_website)
            
            response_data['users'] = [
                {
                    'id': u.id,
                    'username': u.username,
                    'email': u.email,
                    'full_name': u.get_full_name() or u.username,
                    'role': u.role
                }
                for u in users_qs.select_related('website').order_by('username')[:100]  # Limit to 100
            ]
        
        return Response(response_data)


class DropdownOptionsByCategoryView(APIView):
    """
    Get dropdown options for a specific category.
    Useful for loading specific dropdowns on demand.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, category):
        """
        Get dropdown options for a specific category.
        
        Categories:
        - order_configs: All order configuration options
        - enums: All enum choices
        - websites: Website list
        - users: User list (admin only)
        - paper_types, subjects, academic_levels, etc.: Specific config type
        """
        website_id = request.query_params.get('website_id')
        user_website = None
        if request.user.role != 'superadmin':
            user_website = getattr(request.user, 'website', None)
            if user_website:
                website_id = str(user_website.id)
        
        website_filter = Q()
        if website_id:
            website_filter = Q(website_id=website_id)
        elif user_website:
            website_filter = Q(website=user_website)
        
        if category == 'order_configs':
            return Response({
                'paper_types': [
                    {'id': pt.id, 'name': pt.name, 'website_id': pt.website_id}
                    for pt in PaperType.objects.filter(website_filter).select_related('website').order_by('name')
                ],
                'formatting_styles': [
                    {'id': fs.id, 'name': fs.name, 'website_id': fs.website_id}
                    for fs in FormattingandCitationStyle.objects.filter(website_filter).select_related('website').order_by('name')
                ],
                'subjects': [
                    {'id': s.id, 'name': s.name, 'is_technical': s.is_technical, 'website_id': s.website_id}
                    for s in Subject.objects.filter(website_filter).select_related('website').order_by('name')
                ],
                'academic_levels': [
                    {'id': al.id, 'name': al.name, 'website_id': al.website_id}
                    for al in AcademicLevel.objects.filter(website_filter).select_related('website').order_by('name')
                ],
                'types_of_work': [
                    {'id': tow.id, 'name': tow.name, 'website_id': tow.website_id}
                    for tow in TypeOfWork.objects.filter(website_filter).select_related('website').order_by('name')
                ],
                'english_types': [
                    {'id': et.id, 'name': et.name, 'code': et.code, 'website_id': et.website_id}
                    for et in EnglishType.objects.filter(website_filter).select_related('website').order_by('name')
                ],
            })
        
        elif category == 'enums':
            return Response({
                'order_status': [
                    {'value': status.value, 'label': status.name.replace('_', ' ').title()}
                    for status in OrderStatus
                ],
                'payment_status': [
                    {'value': status.value, 'label': status.name.replace('_', ' ').title()}
                    for status in OrderPaymentStatus
                ],
                'payment_status_choices': [
                    {'value': choice[0], 'label': choice[1]}
                    for choice in STATUS_CHOICES
                ],
                'payment_types': [
                    {'value': choice[0], 'label': choice[1]}
                    for choice in PAYMENT_TYPE_CHOICES
                ],
                'spacing_options': [
                    {'value': option.value, 'label': option.name.replace('_', ' ').title()}
                    for option in SpacingOptions
                ],
                'dispute_status': [
                    {'value': status.value, 'label': status.name.replace('_', ' ').title()}
                    for status in DisputeStatusEnum
                ],
                'fine_types': [
                    {'value': choice.value, 'label': choice.label}
                    for choice in FineType
                ],
                'fine_status': [
                    {'value': choice.value, 'label': choice.label}
                    for choice in FineStatus
                ],
            })
        
        elif category == 'websites':
            websites_qs = Website.objects.filter(is_active=True, is_deleted=False)
            if request.user.role != 'superadmin' and user_website:
                websites_qs = websites_qs.filter(id=user_website.id)
            
            return Response([
                {'id': w.id, 'name': w.name, 'domain': w.domain}
                for w in websites_qs.order_by('name')
            ])
        
        elif category == 'users':
            if request.user.role not in ['superadmin', 'admin']:
                return Response({'detail': 'Permission denied'}, status=403)
            
            users_qs = User.objects.filter(is_active=True)
            if request.user.role == 'admin' and user_website:
                users_qs = users_qs.filter(website=user_website)
            
            return Response([
                {
                    'id': u.id,
                    'username': u.username,
                    'email': u.email,
                    'full_name': u.get_full_name() or u.username,
                    'role': u.role
                }
                for u in users_qs.select_related('website').order_by('username')[:100]
            ])
        
        # Specific config types
        elif category == 'paper_types':
            return Response([
                {'id': pt.id, 'name': pt.name, 'website_id': pt.website_id}
                for pt in PaperType.objects.filter(website_filter).select_related('website').order_by('name')
            ])
        
        elif category == 'subjects':
            return Response([
                {'id': s.id, 'name': s.name, 'is_technical': s.is_technical, 'website_id': s.website_id}
                for s in Subject.objects.filter(website_filter).select_related('website').order_by('name')
            ])
        
        elif category == 'academic_levels':
            return Response([
                {'id': al.id, 'name': al.name, 'website_id': al.website_id}
                for al in AcademicLevel.objects.filter(website_filter).select_related('website').order_by('name')
            ])
        
        elif category == 'formatting_styles':
            return Response([
                {'id': fs.id, 'name': fs.name, 'website_id': fs.website_id}
                for fs in FormattingandCitationStyle.objects.filter(website_filter).select_related('website').order_by('name')
            ])
        
        elif category == 'types_of_work':
            return Response([
                {'id': tow.id, 'name': tow.name, 'website_id': tow.website_id}
                for tow in TypeOfWork.objects.filter(website_filter).select_related('website').order_by('name')
            ])
        
        elif category == 'english_types':
            return Response([
                {'id': et.id, 'name': et.name, 'code': et.code, 'website_id': et.website_id}
                for et in EnglishType.objects.filter(website_filter).select_related('website').order_by('name')
            ])
        
        elif category == 'class_duration_options':
            return Response([
                {'id': opt.id, 'class_code': opt.class_code, 'label': opt.label, 'website_id': opt.website_id}
                for opt in ClassDurationOption.objects.filter(website_filter, is_active=True)
                .select_related('website')
                .order_by('website', 'class_code')
            ])
        
        else:
            return Response({'detail': f'Unknown category: {category}'}, status=400)

