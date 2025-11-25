"""
Service for detecting suspected duplicate accounts across websites.
Helps identify clients and writers who may have created multiple accounts.
"""
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, F
from django.db import transaction
from collections import defaultdict
from datetime import timedelta
from django.utils import timezone
import re

User = get_user_model()


class DuplicateAccountDetectionService:
    """
    Detects suspected duplicate accounts using multiple signals:
    - Email similarity (normalized)
    - IP address overlap
    - Name similarity
    - Payment method overlap
    - Cross-website activity patterns
    """
    
    @staticmethod
    def normalize_email(email):
        """Normalize email for comparison (remove dots, lowercase)."""
        if not email:
            return None
        email = email.lower().strip()
        # Remove dots before @ for Gmail-style emails
        if '@' in email:
            local, domain = email.split('@', 1)
            local = local.replace('.', '')
            email = f"{local}@{domain}"
        return email
    
    @staticmethod
    def get_similarity_score(str1, str2):
        """Calculate simple similarity score between two strings."""
        if not str1 or not str2:
            return 0.0
        
        str1 = str1.lower().strip()
        str2 = str2.lower().strip()
        
        if str1 == str2:
            return 1.0
        
        # Check if one contains the other
        if str1 in str2 or str2 in str1:
            return 0.8
        
        # Check for common words
        words1 = set(str1.split())
        words2 = set(str2.split())
        if words1 and words2:
            common = len(words1 & words2)
            total = len(words1 | words2)
            return common / total if total > 0 else 0.0
        
        return 0.0
    
    @staticmethod
    def detect_by_email():
        """Detect accounts with similar/normalized emails."""
        from authentication.models import LoginSession
        
        # Get all users with their normalized emails
        users = User.objects.filter(
            role__in=['client', 'writer']
        ).exclude(email__isnull=True).exclude(email='')
        
        email_groups = defaultdict(list)
        
        for user in users:
            normalized = DuplicateAccountDetectionService.normalize_email(user.email)
            if normalized:
                email_groups[normalized].append(user)
        
        # Find groups with multiple users
        duplicates = []
        for normalized_email, user_list in email_groups.items():
            if len(user_list) > 1:
                # Check if they're on different websites
                websites = set(u.website_id for u in user_list if u.website_id)
                if len(websites) > 1 or len(user_list) > 1:
                    duplicates.append({
                        'type': 'email',
                        'confidence': 'high',
                        'signal': f"Same normalized email: {normalized_email}",
                        'users': user_list,
                        'websites': list(websites),
                    })
        
        return duplicates
    
    @staticmethod
    def detect_by_ip_address(days_back=90):
        """Detect accounts sharing IP addresses."""
        from authentication.models import LoginSession
        from writer_management.models.logs import WriterIPLog
        
        cutoff_date = timezone.now() - timedelta(days=days_back)
        
        # Get IPs from login sessions
        login_ips = LoginSession.objects.filter(
            logged_in_at__gte=cutoff_date,
            ip_address__isnull=False
        ).exclude(ip_address='').values('ip_address', 'user_id').distinct()
        
        # Get IPs from writer logs
        writer_ips = WriterIPLog.objects.filter(
            logged_at__gte=cutoff_date,
            ip_address__isnull=False
        ).exclude(ip_address='').values('ip_address', 'writer__user_id').distinct()
        
        # Group by IP
        ip_to_users = defaultdict(set)
        
        for entry in login_ips:
            if entry['ip_address']:
                ip_to_users[entry['ip_address']].add(entry['user_id'])
        
        for entry in writer_ips:
            if entry['ip_address']:
                ip_to_users[entry['ip_address']].add(entry['writer__user_id'])
        
        # Find IPs used by multiple users
        duplicates = []
        for ip, user_ids in ip_to_users.items():
            if len(user_ids) > 1:
                users = User.objects.filter(id__in=user_ids, role__in=['client', 'writer'])
                if users.count() > 1:
                    websites = set(u.website_id for u in users if u.website_id)
                    duplicates.append({
                        'type': 'ip_address',
                        'confidence': 'medium',
                        'signal': f"Shared IP address: {ip}",
                        'users': list(users),
                        'websites': list(websites),
                        'ip_address': ip,
                    })
        
        return duplicates
    
    @staticmethod
    def detect_by_name_similarity():
        """Detect accounts with similar names."""
        users = User.objects.filter(
            role__in=['client', 'writer']
        ).exclude(
            Q(first_name__isnull=True) | Q(first_name=''),
            Q(last_name__isnull=True) | Q(last_name='')
        )
        
        duplicates = []
        checked_pairs = set()
        
        for user1 in users:
            for user2 in users.exclude(id=user1.id):
                pair_key = tuple(sorted([user1.id, user2.id]))
                if pair_key in checked_pairs:
                    continue
                checked_pairs.add(pair_key)
                
                # Check name similarity
                first_sim = DuplicateAccountDetectionService.get_similarity_score(
                    user1.first_name, user2.first_name
                )
                last_sim = DuplicateAccountDetectionService.get_similarity_score(
                    user1.last_name, user2.last_name
                )
                
                # If both names are similar
                if first_sim > 0.7 and last_sim > 0.7:
                    websites = set()
                    if user1.website_id:
                        websites.add(user1.website_id)
                    if user2.website_id:
                        websites.add(user2.website_id)
                    
                    duplicates.append({
                        'type': 'name_similarity',
                        'confidence': 'medium' if first_sim > 0.8 and last_sim > 0.8 else 'low',
                        'signal': f"Similar names: {user1.get_full_name()} ≈ {user2.get_full_name()}",
                        'users': [user1, user2],
                        'websites': list(websites),
                        'similarity_score': (first_sim + last_sim) / 2,
                    })
        
        return duplicates
    
    @staticmethod
    def detect_by_payment_methods():
        """Detect accounts sharing payment methods (cards, PayPal, etc.)."""
        from order_payments_management.models import OrderPayment
        from client_wallet.models import WalletTransaction
        
        duplicates = []
        
        # Check payment cards (if stored)
        # This is a placeholder - adjust based on your payment model structure
        # You may need to extract card last 4 digits or payment method IDs
        
        # Check wallet transactions for same payment source
        # Group by payment method identifier if available
        
        return duplicates
    
    @staticmethod
    def detect_cross_website_patterns():
        """Detect users active across multiple websites with same credentials."""
        from authentication.models import LoginSession
        
        # Find users who logged into multiple websites
        user_website_counts = LoginSession.objects.values('user_id', 'website_id').distinct().values(
            'user_id'
        ).annotate(
            website_count=Count('website_id', distinct=True)
        ).filter(
            website_count__gt=1,
            user__role__in=['client', 'writer']
        )
        
        duplicates = []
        for entry in user_website_counts:
            user = User.objects.get(id=entry['user_id'])
            websites = LoginSession.objects.filter(
                user=user
            ).values_list('website_id', flat=True).distinct()
            
            # Check if there are other users with same email pattern on those websites
            normalized_email = DuplicateAccountDetectionService.normalize_email(user.email)
            if normalized_email:
                similar_users = User.objects.filter(
                    role=user.role
                ).exclude(id=user.id)
                
                for similar_user in similar_users:
                    similar_normalized = DuplicateAccountDetectionService.normalize_email(similar_user.email)
                    if similar_normalized == normalized_email:
                        duplicates.append({
                            'type': 'cross_website',
                            'confidence': 'high',
                            'signal': f"Same email pattern across websites",
                            'users': [user, similar_user],
                            'websites': list(websites),
                        })
                        break
        
        return duplicates
    
    @staticmethod
    def detect_all(role_filter=None, min_confidence='low'):
        """
        Run all detection methods and aggregate results.
        
        Args:
            role_filter: 'client' or 'writer' to filter by role
            min_confidence: 'low', 'medium', or 'high' minimum confidence level
        """
        all_duplicates = []
        
        # Run all detection methods
        all_duplicates.extend(DuplicateAccountDetectionService.detect_by_email())
        all_duplicates.extend(DuplicateAccountDetectionService.detect_by_ip_address())
        all_duplicates.extend(DuplicateAccountDetectionService.detect_by_name_similarity())
        all_duplicates.extend(DuplicateAccountDetectionService.detect_cross_website_patterns())
        
        # Filter by role if specified
        if role_filter:
            filtered = []
            for dup in all_duplicates:
                if all(u.role == role_filter for u in dup['users']):
                    filtered.append(dup)
            all_duplicates = filtered
        
        # Filter by confidence
        confidence_levels = {'low': 0, 'medium': 1, 'high': 2}
        min_level = confidence_levels.get(min_confidence, 0)
        conf_map = {'low': 0, 'medium': 1, 'high': 2}
        
        filtered = []
        for dup in all_duplicates:
            if conf_map.get(dup.get('confidence', 'low'), 0) >= min_level:
                filtered.append(dup)
        
        # Group duplicates by user sets
        grouped = DuplicateAccountDetectionService._group_duplicates(filtered)
        
        return grouped
    
    @staticmethod
    def _group_duplicates(duplicates):
        """Group duplicate detections that reference the same users."""
        user_groups = defaultdict(list)
        
        for dup in duplicates:
            # Create a key from sorted user IDs
            user_ids = tuple(sorted(u.id for u in dup['users']))
            user_groups[user_ids].append(dup)
        
        # Convert to list format
        grouped = []
        for user_ids, dup_list in user_groups.items():
            users = User.objects.filter(id__in=user_ids)
            
            # Aggregate signals
            signals = [d['signal'] for d in dup_list]
            types = [d['type'] for d in dup_list]
            confidences = [d.get('confidence', 'low') for d in dup_list]
            
            # Determine overall confidence (highest)
            conf_map = {'low': 0, 'medium': 1, 'high': 2}
            max_conf = max(confidences, key=lambda c: conf_map.get(c, 0))
            
            # Get all websites (handle both IDs and objects)
            all_websites = set()
            for dup in dup_list:
                for w in dup.get('websites', []):
                    if w:
                        # If it's an ID, keep as ID; if it's an object, get the ID
                        if isinstance(w, int):
                            all_websites.add(w)
                        else:
                            all_websites.add(w.id if hasattr(w, 'id') else w)
            
            # Convert to website objects for easier access
            from websites.models import Website
            website_objects = Website.objects.filter(id__in=all_websites) if all_websites else []
            
            grouped.append({
                'user_ids': list(user_ids),
                'users': list(users),
                'websites': list(website_objects),
                'website_ids': list(all_websites),
                'signals': signals,
                'detection_types': list(set(types)),
                'confidence': max_conf,
                'match_count': len(dup_list),
                'details': dup_list,
            })
        
        return grouped
    
    @staticmethod
    def get_user_duplicate_summary(user_id):
        """Get all suspected duplicates for a specific user."""
        user = User.objects.get(id=user_id)
        all_duplicates = DuplicateAccountDetectionService.detect_all()
        
        user_duplicates = []
        for dup in all_duplicates:
            if user.id in dup['user_ids']:
                user_duplicates.append(dup)
        
        return user_duplicates

