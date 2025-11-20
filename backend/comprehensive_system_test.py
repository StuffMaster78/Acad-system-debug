#!/usr/bin/env python3
"""
Comprehensive System Test Script
Tests all major functionality across all user roles
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import json

User = get_user_model()

class SystemTester:
    def __init__(self):
        self.client = APIClient()
        self.results = {
            'client': {'passed': [], 'failed': [], 'warnings': []},
            'writer': {'passed': [], 'failed': [], 'warnings': []},
            'admin': {'passed': [], 'failed': [], 'warnings': []},
            'superadmin': {'passed': [], 'failed': [], 'warnings': []},
            'support': {'passed': [], 'failed': [], 'warnings': []},
            'editor': {'passed': [], 'failed': [], 'warnings': []},
        }
        self.test_users = {}
    
    def create_test_users(self):
        """Create or get test users for each role"""
        roles = ['client', 'writer', 'admin', 'superadmin', 'support', 'editor']
        
        for role in roles:
            email = f'test_{role}@example.com'
            username = f'test_{role}'
            
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': username,
                    'role': role,
                    'is_active': True,
                    'is_staff': role in ['admin', 'superadmin', 'support', 'editor'],
                    'is_superuser': role == 'superadmin',
                }
            )
            
            if created:
                user.set_password('testpass123')
                user.save()
            
            self.test_users[role] = user
            print(f"✓ Test user for {role}: {email}")
    
    def test_endpoint(self, role, endpoint_name, method, url, data=None, expected_status=200):
        """Test an API endpoint"""
        try:
            if method == 'GET':
                response = self.client.get(url)
            elif method == 'POST':
                response = self.client.post(url, data, format='json')
            elif method == 'PATCH':
                response = self.client.patch(url, data, format='json')
            elif method == 'DELETE':
                response = self.client.delete(url)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            if response.status_code == expected_status:
                self.results[role]['passed'].append(f"{endpoint_name}: {method} {url}")
                return True, response
            else:
                self.results[role]['failed'].append(
                    f"{endpoint_name}: {method} {url} - Expected {expected_status}, got {response.status_code}"
                )
                return False, response
        except Exception as e:
            self.results[role]['failed'].append(f"{endpoint_name}: {method} {url} - Exception: {str(e)}")
            return False, None
    
    def test_client_functionality(self):
        """Test client role functionality"""
        print("\n" + "="*60)
        print("TESTING CLIENT ROLE")
        print("="*60)
        
        user = self.test_users['client']
        self.client.force_authenticate(user=user)
        
        # Dashboard endpoints
        endpoints = [
            ('Client Dashboard Stats', 'GET', '/api/v1/client-management/dashboard/stats/'),
            ('Client Loyalty', 'GET', '/api/v1/client-management/dashboard/loyalty/'),
            ('Client Analytics', 'GET', '/api/v1/client-management/dashboard/analytics/'),
            ('Client Wallet Analytics', 'GET', '/api/v1/client-management/dashboard/wallet/'),
            ('Client Referrals', 'GET', '/api/v1/client-management/dashboard/referrals/'),
            ('Orders List', 'GET', '/api/v1/orders/orders/'),
            ('Wallet Balance', 'GET', '/api/v1/wallet/wallet/'),
            ('Loyalty Points', 'GET', '/api/v1/loyalty-management/loyalty-points/'),
            ('Notifications', 'GET', '/api/v1/notifications_system/notifications/'),
        ]
        
        for name, method, url in endpoints:
            self.test_endpoint('client', name, method, url, expected_status=[200, 404])
    
    def test_writer_functionality(self):
        """Test writer role functionality"""
        print("\n" + "="*60)
        print("TESTING WRITER ROLE")
        print("="*60)
        
        user = self.test_users['writer']
        self.client.force_authenticate(user=user)
        
        endpoints = [
            ('Writer Dashboard Earnings', 'GET', '/api/v1/writer-management/dashboard/earnings/'),
            ('Writer Performance', 'GET', '/api/v1/writer-management/dashboard/performance/'),
            ('Writer Order Queue', 'GET', '/api/v1/writer-management/dashboard/queue/'),
            ('Writer Badges', 'GET', '/api/v1/writer-management/dashboard/badges/'),
            ('Writer Level', 'GET', '/api/v1/writer-management/dashboard/level/'),
            ('Writer Orders', 'GET', '/api/v1/writer-management/orders/'),
            ('Writer Profile', 'GET', '/api/v1/writer-management/profile/'),
        ]
        
        for name, method, url in endpoints:
            self.test_endpoint('writer', name, method, url, expected_status=[200, 404])
    
    def test_admin_functionality(self):
        """Test admin role functionality"""
        print("\n" + "="*60)
        print("TESTING ADMIN ROLE")
        print("="*60)
        
        user = self.test_users['admin']
        self.client.force_authenticate(user=user)
        
        endpoints = [
            ('Admin Dashboard', 'GET', '/api/v1/admin-management/dashboard/'),
            ('Dashboard Summary', 'GET', '/api/v1/admin-management/dashboard/metrics/summary/'),
            ('Yearly Orders', 'GET', '/api/v1/admin-management/dashboard/metrics/yearly-orders/?year=2025'),
            ('Yearly Earnings', 'GET', '/api/v1/admin-management/dashboard/metrics/yearly-earnings/?year=2025'),
            ('Monthly Orders', 'GET', '/api/v1/admin-management/dashboard/metrics/monthly-orders/?year=2025&month=11'),
            ('Payment Status', 'GET', '/api/v1/admin-management/dashboard/metrics/payment-status/'),
            ('Service Revenue', 'GET', '/api/v1/admin-management/dashboard/metrics/service-revenue/?days=30'),
            ('User Management', 'GET', '/api/v1/users/users/'),
            ('Order Management', 'GET', '/api/v1/orders/orders/'),
            ('Writer Payments', 'GET', '/api/v1/writer-wallet/payments/'),
            ('Activity Logs', 'GET', '/api/v1/activity/activity-logs/'),
        ]
        
        for name, method, url in endpoints:
            self.test_endpoint('admin', name, method, url, expected_status=[200, 404])
    
    def test_superadmin_functionality(self):
        """Test superadmin role functionality"""
        print("\n" + "="*60)
        print("TESTING SUPERADMIN ROLE")
        print("="*60)
        
        user = self.test_users['superadmin']
        self.client.force_authenticate(user=user)
        
        endpoints = [
            ('Superadmin Dashboard', 'GET', '/api/v1/superadmin-management/dashboard/'),
            ('Website Management', 'GET', '/api/v1/websites/websites/'),
            ('All Users', 'GET', '/api/v1/users/users/'),
        ]
        
        for name, method, url in endpoints:
            self.test_endpoint('superadmin', name, method, url, expected_status=[200, 404])
    
    def test_support_functionality(self):
        """Test support role functionality"""
        print("\n" + "="*60)
        print("TESTING SUPPORT ROLE")
        print("="*60)
        
        user = self.test_users['support']
        self.client.force_authenticate(user=user)
        
        endpoints = [
            ('Support Dashboard', 'GET', '/api/v1/support-management/dashboard/'),
            ('Support Tickets', 'GET', '/api/v1/tickets/tickets/'),
            ('Ticket Queue', 'GET', '/api/v1/support-management/tickets/queue/'),
        ]
        
        for name, method, url in endpoints:
            self.test_endpoint('support', name, method, url, expected_status=[200, 404])
    
    def test_editor_functionality(self):
        """Test editor role functionality"""
        print("\n" + "="*60)
        print("TESTING EDITOR ROLE")
        print("="*60)
        
        user = self.test_users['editor']
        self.client.force_authenticate(user=user)
        
        endpoints = [
            ('Editor Dashboard', 'GET', '/api/v1/editor-management/dashboard/stats/'),
            ('Editor Tasks', 'GET', '/api/v1/editor-management/tasks/'),
            ('Available Tasks', 'GET', '/api/v1/editor-management/tasks/available/'),
        ]
        
        for name, method, url in endpoints:
            self.test_endpoint('editor', name, method, url, expected_status=[200, 404])
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("COMPREHENSIVE SYSTEM TEST REPORT")
        print("="*60)
        
        total_passed = sum(len(self.results[role]['passed']) for role in self.results)
        total_failed = sum(len(self.results[role]['failed']) for role in self.results)
        total_warnings = sum(len(self.results[role]['warnings']) for role in self.results)
        
        print(f"\nOverall Statistics:")
        print(f"  ✓ Passed: {total_passed}")
        print(f"  ✗ Failed: {total_failed}")
        print(f"  ⚠ Warnings: {total_warnings}")
        
        for role in ['client', 'writer', 'admin', 'superadmin', 'support', 'editor']:
            print(f"\n{role.upper()} ROLE:")
            print(f"  ✓ Passed: {len(self.results[role]['passed'])}")
            print(f"  ✗ Failed: {len(self.results[role]['failed'])}")
            print(f"  ⚠ Warnings: {len(self.results[role]['warnings'])}")
            
            if self.results[role]['failed']:
                print(f"\n  Failed Tests:")
                for failure in self.results[role]['failed'][:10]:  # Show first 10
                    print(f"    - {failure}")
        
        return {
            'total_passed': total_passed,
            'total_failed': total_failed,
            'total_warnings': total_warnings,
            'results': self.results
        }
    
    def run_all_tests(self):
        """Run all tests"""
        print("Creating test users...")
        self.create_test_users()
        
        self.test_client_functionality()
        self.test_writer_functionality()
        self.test_admin_functionality()
        self.test_superadmin_functionality()
        self.test_support_functionality()
        self.test_editor_functionality()
        
        return self.generate_report()

if __name__ == '__main__':
    tester = SystemTester()
    report = tester.run_all_tests()
    
    # Save report to file
    with open('system_test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n✓ Test report saved to system_test_report.json")
