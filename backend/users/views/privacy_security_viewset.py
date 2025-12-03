"""
Privacy and Security Information ViewSet
Provides standard operation procedures (SOPs) and privacy/security information.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone


class PrivacySecurityViewSet(viewsets.ViewSet):
    """
    ViewSet for privacy and security information and SOPs.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def privacy_policy(self, request):
        """
        Get privacy policy information.
        
        GET /api/users/privacy-security/privacy-policy/
        """
        return Response({
            'title': 'Privacy Policy',
            'last_updated': timezone.now().isoformat(),
            'sections': [
                {
                    'title': 'Information We Collect',
                    'content': [
                        'Personal information (name, email, phone number)',
                        'Account information (username, password)',
                        'Order information and transaction history',
                        'Communication preferences',
                        'Device and usage information',
                        'Location data (if provided)',
                    ]
                },
                {
                    'title': 'How We Use Your Information',
                    'content': [
                        'To provide and improve our services',
                        'To process and fulfill orders',
                        'To communicate with you about your account and orders',
                        'To send marketing communications (with your consent)',
                        'To comply with legal obligations',
                        'To protect our rights and prevent fraud',
                    ]
                },
                {
                    'title': 'Data Sharing',
                    'content': [
                        'We do not sell your personal information',
                        'We may share data with service providers who assist in operations',
                        'We may share data when required by law',
                        'We may share aggregated, anonymized data for analytics',
                    ]
                },
                {
                    'title': 'Data Security',
                    'content': [
                        'We use encryption to protect your data',
                        'We implement access controls and authentication',
                        'We regularly update security measures',
                        'We monitor for security threats',
                    ]
                },
                {
                    'title': 'Your Rights',
                    'content': [
                        'Right to access your personal data',
                        'Right to correct inaccurate data',
                        'Right to delete your data',
                        'Right to restrict processing',
                        'Right to data portability',
                        'Right to object to processing',
                        'Right to withdraw consent',
                    ]
                },
                {
                    'title': 'Data Retention',
                    'content': [
                        'We retain data as long as necessary for business purposes',
                        'Account data is retained while your account is active',
                        'Order data is retained for legal and business requirements',
                        'You can request deletion of your data',
                    ]
                },
            ]
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def security_practices(self, request):
        """
        Get security practices and SOPs.
        
        GET /api/users/privacy-security/security-practices/
        """
        return Response({
            'title': 'Security Practices & Standard Operating Procedures',
            'last_updated': timezone.now().isoformat(),
            'sections': [
                {
                    'title': 'Authentication & Access Control',
                    'content': [
                        'Multi-factor authentication (2FA) is available and recommended',
                        'Strong password requirements enforced',
                        'Session management with automatic timeout',
                        'Account lockout after failed login attempts',
                        'Device fingerprinting for suspicious activity detection',
                        'IP whitelisting available for enhanced security',
                    ]
                },
                {
                    'title': 'Password Security',
                    'content': [
                        'Passwords are hashed using industry-standard algorithms',
                        'Password history prevents reuse of recent passwords',
                        'Password expiration policies can be configured',
                        'Password breach detection using Have I Been Pwned API',
                        'Password strength requirements enforced',
                    ]
                },
                {
                    'title': 'Account Protection',
                    'content': [
                        'Account suspension for security violations',
                        'Probation system for disciplinary actions',
                        'Email change requires admin approval and verification',
                        'Phone number verification available',
                        'Security questions for account recovery',
                        'Account takeover protection mechanisms',
                    ]
                },
                {
                    'title': 'Data Encryption',
                    'content': [
                        'Data in transit encrypted using TLS/SSL',
                        'Sensitive data encrypted at rest',
                        'Security question answers encrypted',
                        'Payment information handled securely',
                    ]
                },
                {
                    'title': 'Privacy Controls',
                    'content': [
                        'Writers see clients as Client ID or pen name only',
                        'Clients see writers as Writer ID or pen name only',
                        'Profile visibility controlled by default system settings',
                        'Admin approval required for profile changes',
                        'Avatar uploads require admin approval',
                    ]
                },
                {
                    'title': 'Monitoring & Logging',
                    'content': [
                        'Login attempts logged with IP addresses',
                        'Account activity audit logs maintained',
                        'Security events monitored and alerted',
                        'Data access logs tracked',
                        'Failed authentication attempts tracked',
                    ]
                },
                {
                    'title': 'Incident Response',
                    'content': [
                        'Security incidents are investigated promptly',
                        'Affected users are notified of security breaches',
                        'Remediation steps are taken immediately',
                        'Post-incident reviews conducted',
                    ]
                },
                {
                    'title': 'Compliance',
                    'content': [
                        'GDPR compliance measures in place',
                        'Data subject rights supported',
                        'Privacy by design principles followed',
                        'Regular security assessments conducted',
                    ]
                },
            ]
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def data_rights(self, request):
        """
        Get information about user data rights.
        
        GET /api/users/privacy-security/data-rights/
        """
        return Response({
            'title': 'Your Data Rights',
            'last_updated': timezone.now().isoformat(),
            'rights': [
                {
                    'name': 'Right to Access',
                    'description': 'You have the right to access your personal data and receive a copy.',
                    'how_to_exercise': 'Contact support or use the account settings to download your data.',
                },
                {
                    'name': 'Right to Rectification',
                    'description': 'You can request correction of inaccurate or incomplete data.',
                    'how_to_exercise': 'Update your profile information or contact support.',
                },
                {
                    'name': 'Right to Erasure',
                    'description': 'You can request deletion of your personal data.',
                    'how_to_exercise': 'Submit an account deletion request through account settings.',
                },
                {
                    'name': 'Right to Restrict Processing',
                    'description': 'You can request that we limit how we use your data.',
                    'how_to_exercise': 'Contact support to request processing restrictions.',
                },
                {
                    'name': 'Right to Data Portability',
                    'description': 'You can receive your data in a structured, machine-readable format.',
                    'how_to_exercise': 'Request data export through account settings.',
                },
                {
                    'name': 'Right to Object',
                    'description': 'You can object to processing of your data for certain purposes.',
                    'how_to_exercise': 'Update your communication preferences or contact support.',
                },
                {
                    'name': 'Right to Withdraw Consent',
                    'description': 'You can withdraw consent for data processing at any time.',
                    'how_to_exercise': 'Update your preferences in account settings.',
                },
            ]
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def cookie_policy(self, request):
        """
        Get cookie policy information.
        
        GET /api/users/privacy-security/cookie-policy/
        """
        return Response({
            'title': 'Cookie Policy',
            'last_updated': timezone.now().isoformat(),
            'sections': [
                {
                    'title': 'What Are Cookies',
                    'content': [
                        'Cookies are small text files stored on your device when you visit our website.',
                        'They help us provide a better user experience and analyze site usage.',
                    ]
                },
                {
                    'title': 'Types of Cookies We Use',
                    'content': [
                        'Essential cookies: Required for site functionality',
                        'Authentication cookies: For login and session management',
                        'Preference cookies: Remember your settings and preferences',
                        'Analytics cookies: Help us understand how visitors use our site',
                    ]
                },
                {
                    'title': 'Managing Cookies',
                    'content': [
                        'You can control cookies through your browser settings',
                        'Disabling cookies may affect site functionality',
                        'Essential cookies cannot be disabled',
                    ]
                },
            ]
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def terms_of_service(self, request):
        """
        Get terms of service information.
        
        GET /api/users/privacy-security/terms-of-service/
        """
        return Response({
            'title': 'Terms of Service',
            'last_updated': timezone.now().isoformat(),
            'sections': [
                {
                    'title': 'Acceptance of Terms',
                    'content': [
                        'By using our service, you agree to these terms of service.',
                        'If you do not agree, please do not use our service.',
                    ]
                },
                {
                    'title': 'User Responsibilities',
                    'content': [
                        'Provide accurate and complete information',
                        'Maintain the security of your account',
                        'Use the service in compliance with applicable laws',
                        'Not engage in fraudulent or harmful activities',
                    ]
                },
                {
                    'title': 'Service Availability',
                    'content': [
                        'We strive for high availability but do not guarantee uninterrupted service',
                        'We may perform maintenance that temporarily affects service',
                        'We reserve the right to modify or discontinue services',
                    ]
                },
                {
                    'title': 'Intellectual Property',
                    'content': [
                        'All content and materials are protected by copyright',
                        'Users retain rights to their own content',
                        'You grant us license to use your content to provide services',
                    ]
                },
                {
                    'title': 'Limitation of Liability',
                    'content': [
                        'We are not liable for indirect or consequential damages',
                        'Our liability is limited to the amount you paid for services',
                        'We are not responsible for third-party services or content',
                    ]
                },
            ]
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def all(self, request):
        """
        Get all privacy and security information.
        
        GET /api/users/privacy-security/all/
        """
        # This would call all the other endpoints and combine them
        # For now, return a summary
        return Response({
            'title': 'Privacy & Security Information',
            'last_updated': timezone.now().isoformat(),
            'available_sections': [
                'privacy-policy',
                'security-practices',
                'data-rights',
                'cookie-policy',
                'terms-of-service',
            ],
            'message': 'Use the individual endpoints to get detailed information for each section.',
        }, status=status.HTTP_200_OK)

